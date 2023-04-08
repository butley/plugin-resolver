import os
import traceback
from typing import List

import openai
import requests
import yaml
import logging
from pydantic import BaseModel

from models import OpenAiUsage, PluginResolutionResponse, RequestDefinition, BaseMessage, HumanEvaluationMessage, \
    AiEvaluationMessage, MessageChain
from path import extract_request_and_response_names, extract_components_yaml_for_path
from file import read_text_file

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

methods = ['get', 'post', 'put', 'delete']


def load_plugin(ai_plugin_url):
    response = requests.get(ai_plugin_url)
    if response.ok:
        return response.json()
    else:
        raise ValueError("Failed to get AI plugin JSON")


def calculate_openai_usage(openai_usage: OpenAiUsage, response):
    if (
            response
            and isinstance(response, dict)
            and response.get("usage") is not None
            and response["usage"].get("prompt_tokens") is not None
            and response["usage"].get("completion_tokens") is not None
            and response["usage"].get("total_tokens") is not None
    ):
        openai_usage.prompt += int(response["usage"]["prompt_tokens"])
        openai_usage.response += int(response["usage"]["completion_tokens"])
        openai_usage.total += int(response["usage"]["total_tokens"])
    return openai_usage


def call_openai(messages, model="gpt-3.5-turbo-0301", temperature=0.0, max_tokens=2000):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    return openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )



class PluginResolver(BaseModel):
    message_chain: MessageChain
    openai_usage: OpenAiUsage

    def perform_chat_conversation(self, context_messages, payload_messages):
        for m in payload_messages:
            self.message_chain.messages.append(HumanEvaluationMessage(content=m))
            context_messages.append({"role": "user", "content": m})

        chat_response = call_openai(messages=context_messages)
        self.openai_usage = calculate_openai_usage(self.openai_usage, chat_response)
        self.message_chain.messages.append(AiEvaluationMessage(content=chat_response.choices[0].message.content))
        return chat_response

    def generate_path(self, paths_section, context_messages, message):
        prompts_messages = context_messages.copy()
        paths_text = yaml.dump(paths_section, default_flow_style=False)
        payload = read_text_file("prompts/prompt_identify_path.txt").format(yaml=paths_text, message=message)
        return self.perform_chat_conversation(prompts_messages, [payload])

    def generate_payload_from_components_and_target_path(self, context_messages, message, components_yaml,
                                                         target_path_yaml):
        prompts_messages = context_messages.copy()
        components_text = yaml.dump(components_yaml, default_flow_style=False)
        request, response = extract_request_and_response_names(target_path_yaml)
        payload = read_text_file("prompts/prompt_generate_request_payload.txt").format(
            yaml=components_text, entity=request, message=message)

        return self.perform_chat_conversation(prompts_messages, [payload])

    def resolve(self, context_messages, message, ai_plugin_url):
        plugin_resolution_response = PluginResolutionResponse()
        try:
            ai_plugin_json = load_plugin(ai_plugin_url)
            plugin_yaml = requests.get(ai_plugin_json['api']['url'])
            plugin_yaml_text = plugin_yaml.text
            plugin_yaml = yaml.safe_load(plugin_yaml_text)

            paths_section = plugin_yaml['paths']
            response = self.generate_path(paths_section, context_messages, message)

            openai_usage = calculate_openai_usage(self.openai_usage, response)
            if response and response != 'nyl':
                plugin_resolution_response.plugin_found = True
                target_path_name = response.choices[0].message.content
                target_path = {path: details for path, details in paths_section.items() if path == target_path_name}
                logger.debug("Path " + target_path_name + " found for plugin: " + plugin_yaml['info']['title'])
                for path, operations in target_path.items():
                    for operation_type in operations:
                        components_yaml = extract_components_yaml_for_path(plugin_yaml, target_path_name)
                        if len(components_yaml) > 0:
                            logger.debug("Components found in plugin: " + plugin_yaml['info']['title'])
                            payload_response = self.generate_payload_from_components_and_target_path(context_messages,
                                                                                                     message,
                                                                                                     components_yaml,
                                                                                                     target_path[
                                                                                                         target_path_name])
                            openai_usage = calculate_openai_usage(openai_usage, payload_response)
                            if response != 'nyl':
                                logger.debug('Payload resolved')
                                plugin_resolution_response.plugin_operation_found = True
                                request_definition = RequestDefinition(
                                    base_url=plugin_yaml['servers'][0]['url'],
                                    path=target_path_name,
                                    method=operation_type,
                                    data=payload_response.choices[0].message.content
                                )
                                plugin_resolution_response.request_definition = request_definition
                                break
                            else:
                                logger.debug('Payload not resolved')
                        else:
                            logger.debug("No components found in plugin: " + plugin_yaml['info'][
                                'title'] + " " + operation_type)

            else:
                print("No path found in plugin: " + plugin_yaml['info']['title'])

            plugin_resolution_response.openai_usage = openai_usage
            plugin_resolution_response.message_chain = self.message_chain
            return plugin_resolution_response

        except Exception as e:
            traceback.print_exc()
            plugin_resolution_response.exception = e
            return plugin_resolution_response

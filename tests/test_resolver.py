from models import MessageChain, OpenAiUsage
from resolver import PluginResolver

system_message = {"role": "system", "content": "User id: 45"}
context_messages = [system_message]

message = 'Remember my mom birthday is January 13th'

message_chain = MessageChain()
openai_usage = OpenAiUsage()

plugin_resolver = PluginResolver(message_chain=message_chain,
                                 openai_usage=openai_usage)

response = plugin_resolver.resolve(context_messages, message, 'https://HOST/.well-known/ai-plugin.json')
print(response)



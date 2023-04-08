## plugin-resolver

The PluginResolver class is a utility for resolving plugins in the context of an AI-based conversation. It is responsible for finding a suitable plugin based on the given context messages and user message. The current implementation makes use of the gpt-3.5-turbo-0301 model and employs custom prompts to evaluate different OpenAPI YAML specifications. It then extracts the relevant information from the plugin's OpenAPI specification and generates a request payload that can be used to call the corresponding API. The class also keeps track of OpenAI usage throughout the process.

### Key features of the PluginResolver:

* `generate_path()`: Generates a path based on the given OpenAPI paths section, context messages, and user message.
* `generate_payload_from_components_and_target_path()`: Given the context messages, user message, and extracted components, this method generates a request payload for the target API.
* `resolve()`: Resolves the appropriate plugin, extracts the relevant path and components, and generates a request payload by calling the appropriate methods. It also calculates the OpenAI usage and updates the PluginResolutionResponse.

The PluginResolver class is designed to be a high-level interface for working with plugins in an AI-driven conversation system. Its main goal is to simplify the process of finding the appropriate plugin, extracting the necessary information, and generating a request payload that can be used to interact with the target API.o work with AI plugins that follow the OpenAPI standard, and it utilizes the AI's natural language understanding capabilities to identify the correct API path and generate request payloads based on user messages

Usage example:

```
system_message = {"role": "system", "content": "User id: 45"}
context_messages = [system_message]

message = 'Remember my mom birthday is January 13th'

response = PluginResolver().resolve(context_messages, message, 'https://host/.well-known/ai-plugin.json')
print(response)
```

### Evaluating the response

The `PluginResolutionResponse` class is a data class that could contain information about the plugin that was resolved, 
the path that was extracted, the components that were extracted, and the request payload that was generated. It also contains information about the OpenAI usage throughout the process.


### Framework

This project will provide base models to be reused in other projects. 
The base models are:

* `BaseMessage`: Base class for all messages
* `HumanMessage`: Class for messages from humans
* `AiMessage`: Class for messages from AI
* `AiEvaluationMessage`: Class for messages from AI evaluation that are used in intermediate steps. 

The `AiEvaluationMessage` are very important because they impose a great weight in the OpenAI API usage.



### Limitations

Given the dynamic nature of the resolver, identifying and using an appropriate authentication mechanism is a challenge.
So, the current implementation only supports unauthenticated APIs.

## Setting up the poetry environment

To set up the poetry environment for this project, follow these steps:

1. Ensure you have [Poetry](https://python-poetry.org/) installed on your system. If not, you can install it using the following command:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Navigate to the project's root directory (where the pyproject.toml file is located).

Install the project dependencies using Poetry:
    
```bash
poetry install
```

Activate the virtual environment created by Poetry:

```bash
poetry shell
```

You should now have a fully configured poetry environment with all necessary dependencies installed.

## Building the wheel file
To build a wheel file for this project, follow these steps:

Ensure you are in the project's root directory.

Build the wheel file using Poetry:
```bash
poetry build -f wheel
```

This will generate a .whl file in the dist folder within the project's root directory.

Importing the wheel file into another project
To import the generated wheel file into another project, follow these steps:

Copy the .whl file from the dist folder of the current project to the root directory of the target project.

Install the wheel file in the target project using pip:
```bash
pip install <wheel-file-name>.whl
```

You can now use the functionality provided by this project in the target project by importing the necessary modules and classes.


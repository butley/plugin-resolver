import re
import yaml

methods = ['get', 'post', 'put', 'delete']


def extract_dependencies(components, component_name, extracted_components):
    if component_name not in extracted_components:
        component = components[component_name]
        extracted_components[component_name] = component
        refs = re.findall(r'#/components/schemas/(\w+)', yaml.dump(component))
        for ref in refs:
            extract_dependencies(components, ref, extracted_components)


def extract_request_and_response_names(path_section):
    request_component = None
    response_component = None

    for operation_type in methods:
        if operation_type in path_section:
            operation = path_section[operation_type]

            if 'requestBody' in operation and operation['requestBody']['required']:
                request_component = \
                    operation['requestBody']['content']['application/json']['schema']['$ref'].split('/')[-1]

            if 'responses' in operation and '200' in operation['responses']:
                response_component = \
                    operation['responses']['200']['content']['application/json']['schema']['$ref'].split('/')[-1]

            break

    return request_component, response_component


def extract_components_yaml_for_path(openapi_yaml, path):
    path_content = openapi_yaml['paths'][path]
    components = openapi_yaml['components']['schemas']
    extracted_components = {}

    for operation in methods:
        if operation in path_content:
            operation_content = path_content[operation]

            if 'requestBody' in operation_content:
                ref = operation_content['requestBody']['content']['application/json']['schema']['$ref']
                component_name = ref.split('/')[-1]
                extract_dependencies(components, component_name, extracted_components)

            if 'responses' in operation_content:
                if '200' in operation_content['responses']:
                    ref = operation_content['responses']['200']['content']['application/json']['schema']['$ref']
                    component_name = ref.split('/')[-1]
                    extract_dependencies(components, component_name, extracted_components)

    components_schema = {
        'components': {
            'schemas': extracted_components
        }
    }
    return components_schema
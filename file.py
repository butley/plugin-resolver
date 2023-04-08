def read_text_file(file_name):
    with open(file_name) as f:
        payload = f.read()

    return payload


def read_lines_text_file(file_name):
    with open(file_name) as f:
        payload = f.readlines()

    return payload

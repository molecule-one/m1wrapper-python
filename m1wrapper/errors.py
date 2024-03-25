import requests

def format_error_message(error):
    if "message" in error and "errors" in error:
        return f'{error["message"]}: {repr(error["errors"])}'
    if "message" in error:
        return f'{error["message"]}'
    if "errors" in error:
        return f'{error["errors"]}'
    else:
        return "unknown error"

def is_json_response(response):
    return response.headers.get('Content-Type', '').startswith('application/json')


def maybe_handle_error(response):
    if response.status_code >= 400 and response.status_code < 500 and is_json_response(response):
        error = format_error_message(response.json())
        raise requests.exceptions.HTTPError(error)
    else:
        response.raise_for_status()


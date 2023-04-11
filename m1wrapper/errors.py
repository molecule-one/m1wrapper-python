import requests

def format_error_message(error):
    if error["message"] and error["errors"]:
        return f'{error["message"]}: {repr(error["errors"])}'
    if error["message"]:
        return f'{error["message"]}'
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


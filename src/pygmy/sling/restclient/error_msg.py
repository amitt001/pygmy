import json


INVALID_TOKEN = dict(error="Access token is invalid.")
INTERNAL_SERVER_ERROR_API = "Something went wrong"


def API_ERROR(error_message):
    try:
        if not isinstance(error_message, dict):
            error_message = json.loads(error_message).get('message')
        else:
            error_message = error_message.get('message')
    except Exception as e:
        error_message = INTERNAL_SERVER_ERROR_API
    return dict(error=error_message)

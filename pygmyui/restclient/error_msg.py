import json


INVALID_TOKEN = dict(error=["Please log in again to continue."])
INTERNAL_SERVER_ERROR_API = ["Something went wrong."]


def API_ERROR(error_message):
    """Method to create error dict. Used for redering error in templates"""
    try:
        if not isinstance(error_message, dict):
            try:
                error_message = json.loads(error_message).get('error')
            except json.decoder.JSONDecodeError:
                pass
        elif isinstance(error_message, dict):
            error_message = error_message.get('error')
    except Exception:
        import traceback
        traceback.print_exc()
        error_message = INTERNAL_SERVER_ERROR_API
    return dict(error=error_message if isinstance(error_message,list) else [error_message])

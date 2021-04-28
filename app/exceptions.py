from http import HTTPStatus


class WebserviceException(Exception):
    """Base class for exceptions."""
    def __init__(self, message='Internal Server Error', code=HTTPStatus.INTERNAL_SERVER_ERROR):
        self.message = message
        self.code = code

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code
from http import HTTPStatus


class WebserviceException(Exception):
    """Base class for exceptions."""
    def __init__(self, message='Internal Server Error', code=HTTPStatus.INTERNAL_SERVER_ERROR):
        self.message = message
        self.code = code


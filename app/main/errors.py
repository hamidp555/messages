from flask import jsonify, make_response
from http import HTTPStatus

from . import main


@main.app_errorhandler(HTTPStatus.NOT_FOUND)
def url_not_found(err):
    return make_response(jsonify(error='not found'), HTTPStatus.NOT_FOUND)

@main.app_errorhandler(HTTPStatus.METHOD_NOT_ALLOWED)
def method_not_found(err):
    return make_response(jsonify(error='method not allowed'), HTTPStatus.METHOD_NOT_ALLOWED)

@main.app_errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def internal_server_error(err):
    return make_response(jsonify(error='internal server error'), HTTPStatus.INTERNAL_SERVER_ERROR)

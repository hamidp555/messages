from flask import jsonify, make_response
from flask import current_app as app
from http import HTTPStatus

from ..exceptions import WebserviceException
from . import api


@api.app_errorhandler(WebserviceException)
def webservice_exception(err):
    return make_response(jsonify(error=err.message), err.code)

@api.app_errorhandler(Exception)
def lobal_exception(_):
    """ Log all exceptions """
    app.logger.exception('Exception')
    raise
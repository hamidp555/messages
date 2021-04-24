from flask import Blueprint
from flask_swagger_ui import get_swaggerui_blueprint
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin


spec = APISpec(
    title="Messages Webservice",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)

swaggerui_manager = get_swaggerui_blueprint(
    '/api/v1//docs',
    '/api/v1/swagger.json',
    config={
        'app_name': "messages-webservice",
        'dom_id': '#swagger-ui',
        'validatorUrl': None,
        'defaultModelsExpandDepth': -1,
        'layout': 'StandaloneLayout',
    },
)

api = Blueprint('api', __name__)

from . import messages, errors

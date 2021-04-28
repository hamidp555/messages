from flask import Flask, jsonify, make_response
from flask_marshmallow import Marshmallow
# from flask_migrate import Migrate
from flask_mongoengine import MongoEngine

from http import HTTPStatus

from .config import config


# db = SQLAlchemy()
db = MongoEngine()
ma = Marshmallow()
# mg = Migrate()


def create_app(config_name):
    """application factory function"""

    app = Flask(__name__)

    with app.app_context():
        app.config.from_object(config[config_name])
        config[config_name].init_app(app)

        db.init_app(app)
        ma.init_app(app)
        # mg.init_app(app, db)

        app.logger.info('Initializing webservice')

        @app.route('/api/v1/healthcheck', methods=['GET'])
        def healthcheck():
            return make_response(jsonify(status='healthy'), HTTPStatus.OK)
       
        try:
            from .main import main as main_blueprint
            app.register_blueprint(main_blueprint)

            from .api import api as api_blueprint
            app.register_blueprint(api_blueprint, url_prefix='/api/v1')

            from .api import swaggerui_manager
            app.register_blueprint(swaggerui_manager)

            from .api import spec
            for fn in app.view_functions:
                spec.path(view=app.view_functions[fn])

        except:
            app.logger.exception('Failed to initialize webservice')
            raise
    
    app.logger.info('Webservice Initialized')

    return app

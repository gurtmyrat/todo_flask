import os
from flask import Flask
from flask_jwt_extended import JWTManager
from api.views.user import users_bp
from api.views.task import tasks_bp
from .config import DevelopmentConfig, TestingConfig

def create_app(config_class=None):
    if not config_class:
        flask_env = os.getenv("FLASK_ENV", "development")
        if flask_env == 'testing':
            config_class = TestingConfig
        else:
            config_class = DevelopmentConfig

    app = Flask(__name__)
    app.config.from_object(config_class)

    jwt = JWTManager(app)

    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(tasks_bp, url_prefix='/api')

    return app

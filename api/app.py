import os
from flask import Flask
from flask_jwt_extended import JWTManager
from .config import Config
from api.views.user import users_bp
from api.views.task import tasks_bp
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)
    jwt = JWTManager(app)
    app.register_blueprint(users_bp)
    app.register_blueprint(tasks_bp)

    return app


app = create_app()

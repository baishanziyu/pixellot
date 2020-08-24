from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_cors import CORS

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = 'no_login.login'


def create_app(config_name):
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .no_login import no_login as no_login_blueprint
    app.register_blueprint(no_login_blueprint)
    return app

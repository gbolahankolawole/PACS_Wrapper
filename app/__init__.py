# FLASK IMPORTS
from flask import Flask
from flask_cors import CORS

# LOCAL IMPORTS
from .config import load_config



def create_app():
    app = Flask(__name__)
    config_class = load_config()
    app.config.from_object(config_class)

    # initialize extensions
    CORS(app, supports_credentials=True)

    # register blueprint/routes
    from .routes import pacs_bp
    from .main import main_bp

    routes_list = [pacs_bp, main_bp]
    for route_instance in routes_list: app.register_blueprint(route_instance)


    return app




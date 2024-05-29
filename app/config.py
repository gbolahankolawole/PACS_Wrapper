import os
from dotenv import load_dotenv

load_dotenv()

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
temp_folder = os.path.join(APP_ROOT, 'temp_images')
os.makedirs(temp_folder, exist_ok=True)
parent_folder = os.path.abspath(f'{APP_ROOT}/..')


class Config:
    """Base config."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'pacswrapper')
    CORS_HEADERS = 'Content-Type'
    TEMP_FOLDER = temp_folder


class DevConfig(Config):
    """Development config. For venv on local"""
    FLASK_ENV = "development"
    FLASK_DEBUG = True


class TestConfig(Config):
    """Testing config. for docker in local"""
    TESTING = True
    FLASK_DEBUG = True


class ProdConfig(Config):
    """Production config."""
    FLASK_ENV = "production"
    FLASK_DEBUG = False


config_classes={"development":DevConfig, "testing": TestConfig,
                "production": ProdConfig}

def load_config():
    ENVIRONMENT = os.environ.get("ENVIRONMENT", 'production')
    env_config = config_classes[ENVIRONMENT.lower()]
    return env_config




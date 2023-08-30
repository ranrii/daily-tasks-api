import os

from app.config import Config
from instance.secrets import secret_key


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("POSTGRESQL_URI", "sqlite:///task.db")
    SECRET_KEY = os.environ.get("SECRET_KEY", secret_key)
    TESTING = True

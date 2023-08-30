import os

from app.config import Config


class DeploymentConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("POSTGRESQL_URI", "sqlite:///task.db")
    SECRET_KEY = os.environ.get("SECRET_KEY")
import os

from app.config import Config
import instance.secrets as i


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("POSTGRESQL_URI", "sqlite:///task.db")
    SECRET_KEY = os.environ.get("SECRET_KEY", i.secret_key)
    TESTING = True
    REAL_MAIL = True
    EMAIL = i.email
    M_PW = i.email_pw

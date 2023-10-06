import os

from app.config import Config
import instance.secrets as i


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("POSTGRESQL_URI", "sqlite:///task.db")
    SECRET_KEY = os.environ.get("SECRET_KEY", i.secret_key)
    ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET", i.access_token_secret)
    REFRESH_TOKEN_SECRET = os.environ.get("REFRESH_TOKEN_SECRET", i.refresh_token_secret)
    RESET_PASSWORD_SECRET = os.environ.get("RESET_PASSWORD_SECRET", i.reset_password_secret)
    TESTING = True
    EMAIL = i.email
    M_PW = i.email_pw
    NO_EXP_TOKEN = True

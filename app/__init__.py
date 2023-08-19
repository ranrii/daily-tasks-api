from flask import Flask

from app.extensions import db
from app.routes.error import error_bp
from app.routes.search import search_bp
from app.routes.task import task_bp
from app.routes.topic import topic_bp


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///task.db"

    db.app = app
    db.init_app(app)

    app.register_blueprint(task_bp)
    app.register_blueprint(topic_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(error_bp)
    return app

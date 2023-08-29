from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from app.extensions import db
from app.routes.auth import auth_bp
from app.routes.error import error_bp
from app.routes.search import search_bp
from app.routes.task import task_bp
from app.routes.topic import topic_bp


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("../instance/config.py")
    CORS(app)
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    with app.app_context():
        db.create_all()
    app.register_blueprint(task_bp)
    app.register_blueprint(topic_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(error_bp)
    app.register_blueprint(auth_bp)
    return app

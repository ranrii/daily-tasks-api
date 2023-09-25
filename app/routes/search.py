from flask import Blueprint, request, jsonify, abort
from sqlalchemy import func, select, and_, or_

from app import db
from app.middleware.auth import jwt_required
from app.models.task import Task
from app.models.topic import Topic
from app.models.user import User

from utils.text import limit_whitespace

search_bp = Blueprint("search", __name__, url_prefix="/search")


@search_bp.route("/topic", methods=["GET"])
@jwt_required()
def topic_search(current_user):
    search_title = limit_whitespace(request.args.get("title"))
    if search_title is None:
        return abort(400, "You must provide 'title' for your search")

    cursor = select(Topic).where(Topic.users.contains(current_user))
    results = search(Topic, cursor, search_title)

    response = {
        "no_of_topic": len(results),
        "topics": [topic.to_dict() for topic in results]
    }
    return jsonify(response), 200


@search_bp.route("/task", methods=["GET"])
@jwt_required()
def task_search(current_user):
    search_title = limit_whitespace(request.args.get("title"))
    topic_id = limit_whitespace(request.args.get("topic_id"))
    if search_title is None:
        return abort(400, "You must provide 'title' for your search")

    cursor = select(Task).where(Task.users.contains(current_user))

    try:
        topic_id = int(topic_id)
        cursor = cursor.where(Task.topic_id == topic_id)
    except TypeError:
        cursor = cursor

    results = search(Task, cursor, search_title)

    tasks = {
        "results": len(results),
        "tasks": [task.to_dict() for task in results]
    }
    return jsonify(tasks), 200


@search_bp.route("/user", methods=["GET"])
@jwt_required()
def user_search(current_user):
    name = limit_whitespace(request.args.get("username"))
    if name is None:
        return abort(400, "`username` is required")
    cursor = select(User).where(User.username.like(f"%{name}%"))
    results = db.session.scalars(cursor).all()
    users = [user.to_dict() for user in results]
    return jsonify(users), 200


def search(resource, cursor, term):
    search_cursor = cursor.filter(resource.title.like(f"%{term}%"))
    ordered = search_cursor.order_by(func.coalesce(resource.last_update, resource.created_at))
    result = db.session.scalars(ordered).all()
    return result

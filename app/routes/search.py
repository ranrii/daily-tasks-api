from flask import Blueprint, request, jsonify, abort
from sqlalchemy import func
from app.models.task import Task
from app.models.topic import Topic
from utils import limit_whitespace

search_bp = Blueprint("search", __name__, url_prefix="/search")


@search_bp.route("/topic", methods=["GET"])
def topic_search():
    search_query = limit_whitespace(request.args.get("title"))
    result = Topic.query.filter(Topic.title.like(f"%{search_query}%"))
    result = result.order_by(func.coalesce(Topic.last_update, Topic.created_at)).all()
    response = {
        "no_of_topic": len(result),
        "topics": [topic.to_dict() for topic in result]
    }
    return jsonify(response), 200


@search_bp.route("/task", methods=["GET"])
def task_search():
    search_title = limit_whitespace(request.args.get("title"))
    if not search_title:
        return abort(400, "You must provide 'title' for your search")

    topic_id = limit_whitespace(request.args.get("topic_id"))
    if topic_id is not None:
        try:
            topic_id = int(topic_id)
        except ValueError:
            return abort(400, "invalid 'topic_id' provided")
        results = Task.query.filter_by(topic_id=topic_id).filter(Task.title.like(f"%{search_title}%"))
        results = results.order_by(func.coalesce(Task.last_update, Task.created_at)).all()
        tasks = {
            "no_of_results": len(results),
            "tasks": [task.to_dict() for task in results]}
        return jsonify(tasks), 200

    results = Task.query.filter(Task.title.like(f"%{search_title}%"))
    results = results.order_by(func.coalesce(Task.last_update, Task.created_at)).all()
    tasks = {
        "results": len(results),
        "tasks": [task.to_dict() for task in results]
    }
    return jsonify(tasks), 200

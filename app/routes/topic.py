import pytz
from flask import Blueprint, jsonify, request, abort
from app.models.topic import Topic
from sqlalchemy import func
from utils import limit_whitespace
from app.extensions import db
from datetime import datetime

topic_bp = Blueprint("topic", __name__, url_prefix="/topic")


@topic_bp.route("/search", methods=["GET"])
def search_topic():
    search_query = limit_whitespace(request.args.get("title"))
    result = Topic.query.filter(Topic.title.like(f"%{search_query}%"))
    result = result.order_by(func.coalesce(Topic.last_update, Topic.created_at)).all()
    response = {
        "no_of_topic": len(result),
        "topics": [topic.to_dict() for topic in result]
    }
    return jsonify(response), 200


@topic_bp.route("", methods=["GET"])
def all_topic():
    result = Topic.query.order_by(func.coalesce(Topic.last_update, Topic.created_at)).all()
    topics = {
        "no_of_topic": len(result),
        "topics": [topic.to_dict() for topic in result]
    }
    return jsonify(topics), 200


@topic_bp.route("", methods=["POST"])
def add_topic():
    timestamp = datetime.now(pytz.utc).replace(microsecond=0)
    data = request.form.to_dict()
    title = limit_whitespace(data.get("title"))
    emoji = limit_whitespace(data.get("emoji"))
    include = limit_whitespace(data.get("include", "false")).lower() == "true"
    if [title, emoji] == [None, None]:
        return abort(400, "You must provide 'title' and 'emoji' for your new topic")

    new_topic = Topic(
        title=limit_whitespace(title),
        emoji=emoji,
        created_at=timestamp,
    )
    db.session.add(new_topic)
    db.session.commit()
    if include:
        return jsonify({"success": f"successfully add new topic",
                        "topic": new_topic.to_dict()}), 200
    return jsonify({"success": f"successfully add new topic", "topic_id": new_topic.id}), 200


@topic_bp.route("", methods=["PUT"])
def update_topic():
    data = request.form.to_dict()
    topic_id = limit_whitespace(data.get("topic_id"))
    try:
        topic_id = int(topic_id)
    except ValueError:
        return abort(400, "invalid 'topic_id' provided")
    new_title = limit_whitespace(data.get("title"))
    new_emoji = limit_whitespace(data.get("emoji"))
    topic = Topic.query.filter_by(id=topic_id).first()
    include = limit_whitespace(data.get("include", "false")).lower() == "true"
    if topic is None:
        return abort(404, f"no topic with id={topic_id} to update")
    if [new_title, new_emoji] == [None, None]:
        return abort(400, "you must provide 'title' or 'emoji' to update")

    if new_title is not None and new_title != topic.title:
        topic.title = new_title
    if new_emoji is not None and new_emoji != topic.emoji:
        topic.emoji = new_emoji
    else:
        return jsonify(caution={"message": "you provided same data as in the database and nothing got updated"})

    topic.last_update = datetime.now(pytz.utc).replace(microsecond=0)
    db.session.commit()
    if include:
        return jsonify({"success": f"successfully updated a topic",
                        "topic": topic.to_dict()}), 200
    return jsonify({"success": f"successfully updated a topic", "topic_id": {topic.id}}), 200


@topic_bp.route("", methods=["DELETE"])
def delete_topic():
    data = request.form.to_dict()
    topic_id = limit_whitespace(data.get("topic_id"))
    topic_title = limit_whitespace(data.get("title"))
    remove_tasks = limit_whitespace(data.get("delete_tasks", "true")) == "true"
    try:
        topic_id = int(topic_id)
    except ValueError:
        return abort(400, "invalid 'topic_id' provided")
    if topic_id is None:
        return abort(400, f"you must provide {topic_id} to remove")

    topic = Topic.query.filter_by(id=topic_id).first()
    if topic is None:
        return abort(404, f"no topic with id={topic_id} found")
    if topic_title != topic.title:
        return abort(400, "topic title is not match")

    removed_tasks = 0
    orphaned_tasks = None
    if remove_tasks:
        for task in topic.tasks:
            db.session.delete(task)
            removed_tasks += 1
    else:
        orphaned_tasks = [task.to_dict() for task in topic.tasks]
    db.session.delete(topic)
    db.session.commit()

    response = {
        "success": "successfully removed a topic and all tasks associated with it",
        "removed_topic": {"id": topic.id, "title": topic.title},
        "tasks_removed": removed_tasks
    }

    if orphaned_tasks is not None:
        response["success"] = "successfully removed a topic and there are orphaned tasks left"
        response["orphaned_tasks"] = orphaned_tasks
    return jsonify(response)

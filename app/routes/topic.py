from flask import Blueprint, jsonify, request, abort

from app.middleware.auth import jwt_required
from app.middleware.permissions import check_permission, grant_permission
from app.models.topic import Topic
from sqlalchemy import func, select
from utils.text import limit_whitespace
from app.extensions import db

topic_bp = Blueprint("topic", __name__, url_prefix="/topic")


@topic_bp.route("", methods=["GET"])
@jwt_required()
def all_topic(current_user):
    selector = select(Topic).where(Topic.users.contains(current_user))
    order = func.coalesce(Topic.last_update, Topic.created_at)
    result = db.session.scalars(selector.order_by(order)).all()

    topics = {
        "no_of_topic": len(result),
        "topics": [topic.to_dict() for topic in result]
    }
    return jsonify(topics), 200


@topic_bp.route("", methods=["POST"])
@jwt_required()
def add_topic(current_user):
    data = request.form.to_dict()
    title = limit_whitespace(data.get("title"))
    emoji = limit_whitespace(data.get("emoji"))
    include = limit_whitespace(data.get("include", "false")).lower() == "true"
    if [title, emoji] == [None, None]:
        return abort(400, "You must provide 'title' and 'emoji' for your new topic")

    new_topic = Topic(
        title=title,
        emoji=emoji,
        creator=current_user
    )
    new_topic.progression_calc()
    db.session.add(new_topic)
    db.session.flush()
    grant_permission(current_user, new_topic, "creator")
    db.session.commit()
    topic = db.session.scalar(select(Topic).where(Topic.id == new_topic.id))

    if topic is None:
        return abort(500, "seems like the topic was not created, please consult developer")
    if include:
        return jsonify({"success": f"successfully add new topic",
                        "topic": topic.to_dict()}), 201
    return jsonify({"success": f"successfully add new topic", "topic_id": new_topic.id}), 201


@topic_bp.route("", methods=["PUT"])
@jwt_required()
def update_topic(current_user):
    data = request.form.to_dict()
    topic_id = limit_whitespace(data.get("topic_id"))

    try:
        topic_id = int(topic_id)
    except ValueError:
        return abort(400, "invalid 'topic_id' provided")

    topic = db.session.scalar(select(Topic).where(Topic.id == topic_id))

    new_title = limit_whitespace(data.get("title"))
    new_emoji = limit_whitespace(data.get("emoji"))
    include = limit_whitespace(data.get("include", "false")).lower() == "true"

    if topic is None:
        return abort(404, f"no topic with id={topic_id} to update")

    check_permission(current_user, topic, ["creator", "moderator"])

    if [new_title, new_emoji] == [None, None]:
        return abort(400, "you must provide 'title' or 'emoji' to update")

    if new_title is not None and new_title != topic.title:
        topic.title = new_title
    if new_emoji is not None and new_emoji != topic.emoji:
        topic.emoji = new_emoji
    else:
        return jsonify(caution={"message": "you provided same data as in the database and nothing got updated"})

    db.session.commit()
    if include:
        updated_topic = Topic.query.filter_by(id=topic.id).first()
        return jsonify({"success": f"successfully updated a topic",
                        "topic": updated_topic.to_dict()}), 200
    return jsonify({"success": f"successfully updated a topic", "topic_id": {topic.id}}), 200


@topic_bp.route("", methods=["DELETE"])
@jwt_required()
def delete_topic(current_user):
    data = request.form.to_dict()
    topic_id = limit_whitespace(data.get("topic_id"))
    topic_title = limit_whitespace(data.get("title"))

    try:
        topic_id = int(topic_id)
    except ValueError:
        return abort(400, "invalid 'topic_id' provided")
    if topic_id is None:
        return abort(400, f"you must provide {topic_id} to remove")

    topic = db.session.scalar(select(Topic).where(Topic.id == topic_id))
    check_permission(current_user, topic, ["creator"])

    if topic is None:
        return abort(404, f"no topic with id={topic_id} found")
    if topic_title != topic.title:
        return abort(400, "topic title is not match")

    db.session.delete(topic)
    db.session.commit()

    response = {
        "success": "successfully removed a topic and all tasks associated with it",
        "removed_topic": {"id": topic.id, "title": topic.title}
    }
    return jsonify(response), 200

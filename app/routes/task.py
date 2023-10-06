import pytz
from flask import Blueprint, abort, jsonify, request, g
from sqlalchemy import select, and_

from app.extensions import db
from app.middleware.auth import jwt_required
from app.middleware.permissions import check_permission, grant_permission
from app.models.task import Task
from app.models.topic import Topic
from app.routes import get_user
from utils.text import limit_whitespace, dt_from_string

task_bp = Blueprint("task", __name__, url_prefix="/topic/<int:topic_id>")


@task_bp.before_request
def load_topic():
    topic_id = request.view_args.get("topic_id")
    if topic_id is None:
        return jsonify(error={"code": 400, "message": "no `topic_id` provided"}), 400

    topic = db.session.scalar(select(Topic).where(Topic.id == topic_id))

    if topic is None:
        return jsonify(error={"code": 404, "message": f"topic id {topic_id} not found"}), 404
    topic.progression_calc()
    g.topic = topic


@task_bp.route("/task", methods=["GET"])
@jwt_required()
def all_task(current_user, topic_id):
    check_permission(current_user, g.topic, ["user"])
    result = g.topic.tasks
    if result is None:
        return abort(404, f"not found tasks associated with topic id={g.topic.id}")
    response = {
        "num_of_tasks": len(result),
        "tasks": [task.to_dict() for task in result]
    }
    return jsonify(response), 200


@task_bp.route("/task", methods=["POST"])
@jwt_required()
def add_task(current_user, topic_id):
    check_permission(current_user, g.topic, ["creator", "moderator"])

    data = request.form.to_dict()
    title = limit_whitespace(data.get("title"))
    detail = limit_whitespace(data.get("detail"))
    emoji = limit_whitespace(data.get("emoji"))
    due_time = dt_from_string(limit_whitespace(data.get("due_time")))
    status = limit_whitespace(data.get("status", "Unknown"))
    include = limit_whitespace(data.get("include", "false")).lower() == "true"

    possible_status = ["NextUp", "InProgress", "Complete", "Unknown"]
    if status not in possible_status:
        return abort(400, f"invalid status provided can only be one of: {possible_status}")
    if None in [title, detail, emoji, due_time, status]:
        return abort(400, "'title', 'due_time', 'detail' and 'emoji' values are required")

    new_task = Task(
        title=title,
        detail=detail,
        emoji=emoji,
        due_time=due_time,
        status=status,
        topic=g.topic,
        creator=current_user
    )
    db.session.add(new_task)
    g.topic.progression_calc()
    db.session.flush()
    grant_permission(g.topic.creator, new_task, "topicOwner")
    if current_user is not g.topic.creator:
        grant_permission(current_user, new_task, "creator")

    db.session.commit()

    if include:
        return jsonify(
            {
                "success": f"successfully added a new task",
                "added_task": new_task.to_dict()
            }
        ), 201
    return jsonify(
        {
            "success": f"successfully added a new task",
            "task_id": new_task.id,
            "topic_id": new_task.topic.id
        }
    ), 201


@task_bp.route("/task", methods=["PUT"])
@jwt_required()
def edit_task(current_user, topic_id):
    data = request.form.to_dict()
    task_id = limit_whitespace(data.get("task_id"))
    try:
        task_id = int(task_id)
    except ValueError:
        return abort(400, "invalid 'task_id' provided")
    if task_id is None:
        return abort(400, "you must provide 'task_id' to update")
    task = db.session.scalar(select(Task).where(and_(Task.topic == g.topic, Task.id == task_id)))
    if task is None:
        return abort(404, f"no such task with task id={task_id} found")
    check_permission(current_user, [task, g.topic], ["user"])

    new_title = limit_whitespace(data.get("title"))
    new_detail = limit_whitespace(data.get("detail"))
    new_emoji = limit_whitespace(data.get("emoji"))
    new_due_time = dt_from_string(limit_whitespace(data.get("due_time")))
    new_status = limit_whitespace(data.get("status"))
    include = limit_whitespace(data.get("include", "false")).lower() == "true"

    if [new_title, new_detail, new_emoji, new_due_time, new_status] is [None, None, None, None, None]:
        return abort(400, "you must provide 'title', 'detail', 'emoji', 'due_time' or 'status' to update")

    possible_status = ["NextUp", "InProgress", "Complete", "Unknown"]
    if new_status is not None and new_status not in possible_status:
        return abort(400, f"invalid status provided can only be one of: {possible_status}")

    changes = False

    if new_status is not None and new_status != task.status:
        task.status = new_status
        changes = changes or True
    check_permission(current_user, task, ["creator", "moderator", "topicOwner"])
    if new_title is not None and new_title != task.title:
        task.title = new_title
        changes = changes or True
    if new_detail is not None and new_detail != task.detail:
        task.detail = new_detail
        changes = changes or True
    if new_emoji is not None and new_emoji != task.emoji:
        task.emoji = new_emoji
        changes = changes or True
    if new_due_time is not None and new_due_time != task.due_time.replace(tzinfo=pytz.utc):
        task.due_time = new_due_time
        changes = changes or True

    if not changes:
        return jsonify(caution={"message": "you provided same data as in the database and nothing got updated"})

    g.topic.progression_calc()
    db.session.commit()
    if include:
        updated_task = Task.query.filter_by(id=task.id).first()
        return jsonify({"success": f"successfully updated a task",
                        "task": updated_task.to_dict()})
    return jsonify({"success": f"successfully updated a task", "task_id": task.id, "topic_id": task.topic.id})


@task_bp.route("/task", methods=["DELETE"])
@jwt_required()
def delete_task(current_user, topic_id):
    data = request.form.to_dict()
    task_id = limit_whitespace(data.get("task_id"))
    try:
        task_id = int(task_id)
    except ValueError:
        return abort(400, "invalid 'task_id' provided")

    task_title = limit_whitespace(data.get("title"))
    task = db.session.scalar(select(Task).where(and_(Task.id == task_id, Task.topic == g.topic)))
    if task is None:
        return abort(404, f"no such task with id={task_id} associated with topic id={g.topic.id} is found")
    if current_user not in [task.creator, g.topic.creator]:
        return abort(403, "only topic creator and task creator can delete this task")
    if task_title != task.title:
        return abort(400, "provided task title are not matched")
    db.session.delete(task)
    db.session.commit()
    return jsonify({"success": f"successfully removed a task", "task": {"id": task.id, "title": task.title}}), 200


@task_bp.route("/contribute", methods=["PUT"])
@jwt_required()
def contribute(current_user, topic_id):
    contributor_id = request.form.get("user_id")
    if contributor_id is None:
        return abort(400, "`user_id` is required")
    if contributor_id == current_user.id:
        return abort(400, "you already have permission")
    role = request.form.get("role", "user")
    if role not in ["user", "moderator"]:
        return abort(403, "only 'user' and 'moderator' are allowed to set the user's role")
    check_permission(current_user, g.topic, ["creator", "moderator"])
    contributor = get_user(contributor_id)
    grant_permission(contributor, g.topic, role)
    db.session.commit()
    return jsonify({"success": f"added the user {contributor.username} to the topic {g.topic.id}"}), 201


@task_bp.route("/task/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task(current_user, task_id, topic_id):
    task = db.session.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        return abort(404, "task not found")
    check_permission(current_user, task, ["user"])
    return jsonify(task.to_dict), 200


@task_bp.route("/task/<int:task_id>/contribute", methods=["PUT"])
@jwt_required()
def task_contribute(current_user, task_id, topic_id):
    contributor_id = request.form.get("user_id")
    if contributor_id is None:
        return abort(400, "`user_id` is required")
    if current_user.id == contributor_id:
        return abort(400, "you already granted permission")
    role = request.form.get("role", "user")
    task = db.session.scalar(select(Task).where(Task.id == task_id))

    # creator/moderators of this task or topic are allowed
    check_permission(current_user, [task, g.topic], ["creator", "moderator", "topicOwner"])
    if task is None:
        return abort(404, "task not found")

    contributor = get_user(contributor_id)
    grant_permission(contributor, task, role)
    if contributor not in g.topic.users:
        grant_permission(contributor, g.topic, "user")
    db.session.commit()
    return jsonify({"success": f"added the user {contributor.username} to the task {task_id}"}), 201

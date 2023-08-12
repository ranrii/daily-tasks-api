from datetime import datetime

import pytz
from flask import Blueprint, abort, jsonify, request
from sqlalchemy import func

from app.extensions import db
from app.models.task import Task
from app.models.topic import Topic
from utils import limit_whitespace, dt_from_string

task_bp = Blueprint("task", __name__, url_prefix="/topic/<int:topic_id>/task")


@task_bp.route("", methods=["GET"])
def all_task(topic_id):
    result = Task.query.filter_by(topic_id=topic_id).order_by(func.coalesce(Task.last_update, Task.created_at)).all()
    if result is None:
        return abort(404, f"not found tasks associated with topic id={topic_id}")
    response = {
        "num_of_tasks": len(result),
        "tasks": [task.to_dict() for task in result]
    }
    return jsonify(response), 200


@task_bp.route("", methods=["POST"])
def add_task(topic_id):
    topic = Topic.query.filter_by(id=topic_id).first()
    if topic is None:
        return abort(
            404,
            f"no topic with id={topic_id} found, you may need to create new topic before creating new task"
        )

    data = request.form.to_dict()
    title = limit_whitespace(data.get("title"))
    detail = limit_whitespace(data.get("detail"))
    emoji = limit_whitespace(data.get("emoji"))
    due_time = dt_from_string(limit_whitespace(data.get("due_time")))
    status = limit_whitespace(data.get("status"))
    include = limit_whitespace(data.get("include", "false")).lower() == "true"

    possible_status = ["NextUp", "InProgress", "Complete", "Unknown"]
    if status not in possible_status:
        return abort(400, f"invalid status provided can only be one of: {possible_status}")
    if None in [title, detail, emoji, due_time, status]:
        return abort(400, "'title', 'due_time', 'detail' and 'emoji' values are required")

    timestamp = datetime.now(pytz.utc).replace(microsecond=0)
    new_task = Task(
        title=title,
        detail=detail,
        emoji=emoji,
        due_time=due_time,
        status=status,
        created_at=timestamp,
        topic=topic
    )
    db.session.add(new_task)
    db.session.commit()
    if include:
        return jsonify(
            {
                "success": f"successfully added a new task",
                "added_task": new_task.to_dict()
             }
        ), 200
    return jsonify(
        {
            "success": f"successfully added a new task",
            "task_id": new_task.id,
            "topic_id": new_task.topic.id
        }
    ), 200


@task_bp.route("/topic/<int:topic_id>/task", methods=["PUT"])
def edit_task(topic_id):
    data = request.form.to_dict()
    task_id = limit_whitespace(data.get("task_id"))
    try:
        task_id = int(task_id)
    except ValueError:
        return abort(400, "invalid 'task_id' provided")
    if task_id is None:
        return abort(400, "you must provide 'task_id' to update")
    task = Task.query.filter_by(topic_id=topic_id, id=task_id).first()
    if task is None:
        return abort(404, f"no such task with task id={task_id} found")

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

    if new_status is not None and new_status != task.status:
        task.status = new_status
    if new_title is not None and new_title != task.title:
        task.title = new_title
    if new_detail is not None and new_detail != task.detail:
        task.detail = new_detail
    if new_emoji is not None and new_emoji != task.emoji:
        task.emoji = new_emoji
    if new_due_time is not None and new_due_time != task.due_time.replace(tzinfo=pytz.utc):
        task.due_time = new_due_time
    else:
        return jsonify(caution={"message": "you provided same data as in the database and nothing got updated"})

    task.last_update = datetime.now(pytz.utc).replace(microsecond=0)
    db.session.commit()
    if include:
        return jsonify({"success": f"successfully updated a task",
                        "task": task.to_dict()})
    return jsonify({"success": f"successfully updated a task", "task_id": task.id, "topic_id": task.topic.id})


@task_bp.route("", methods=["DELETE"])
def delete_task(topic_id):
    data = request.form.to_dict()
    task_id = limit_whitespace(data.get("task_id"))
    try:
        task_id = int(task_id)
    except ValueError:
        return abort(400, "invalid 'task_id' provided")
    task_title = limit_whitespace(data.get("title"))
    task = Task.query.filter_by(id=task_id, topic_id=topic_id).first()
    if task is None:
        return abort(404, f"no such task with id={task_id} associated with topic id={topic_id} is found")
    if task_title != task.title:
        return abort(400, "provided task title are not matched")
    db.session.delete(task)
    db.session.commit()
    return jsonify({"success": f"successfully removed a task", "task": {"id": task.id, "title": task.title}}), 200

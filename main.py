import os
from datetime import datetime
import pytz
from dotenv import load_dotenv
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from utils import limit_whitespace, dt_from_string

# TODO: Remove below dependencies before deployment
from model import db, Topic, Task
load_dotenv()


app = Flask(__name__)
cors = CORS(app)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///task.db")
debug = os.environ.get("DEBUG") == "TRUE"
db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()


@app.errorhandler(400)
def bad_request(error):
    return jsonify(error={"code": 400, "message": error.description}), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify(error={"code": 404, "message": error.description}), 404


@app.errorhandler(401)
def unauthorized(error):
    return jsonify(error={"code": 401, "message": error.description}), 401


@app.errorhandler(415)
def unsupported(error):
    return jsonify(error={"code": 415, "message": "please format your data in the dictionary-typed/json format"})


@app.route("/topic", methods=["GET"])
def all_topic():
    result = Topic.query.all()
    topics = {
        "no_of_topic": len(result),
        "topics": [topic.to_dict() for topic in result]
    }
    return jsonify(topics), 200


@app.route("/topic/search", methods=["GET"])
def search_topic():
    search_query = limit_whitespace(request.args.get("title"))
    result = Topic.query.filter(Topic.title.like(f"%{search_query}%")).all()
    response = {
        "no_of_topic": len(result),
        "topics": [topic.to_dict() for topic in result]
    }
    return jsonify(response), 200


@app.route("/topic", methods=["POST"])
def add_topic():
    timestamp = datetime.now(pytz.utc).replace(microsecond=0)
    data = request.form.to_dict()
    title = limit_whitespace(data.get("title"))
    description = limit_whitespace(data.get("description"))
    include = limit_whitespace(data.get("include", "false")).lower() == "true"
    if title is None:
        return abort(400, "You must provide 'title' for your new topic")

    new_topic = Topic(
        title=limit_whitespace(title),
        description=description,
        created_at=timestamp,
    )
    db.session.add(new_topic)
    db.session.commit()
    if include:
        return jsonify({"success": f"successfully add new topic",
                        "topic": new_topic.to_dict()}), 200
    return jsonify({"success": f"successfully add new topic", "topic_id": new_topic.id}), 200


@app.route("/topic", methods=["PUT"])
def update_topic():
    data = request.form.to_dict()
    topic_id = limit_whitespace(data.get("topic_id"))
    try:
        topic_id = int(topic_id)
    except ValueError:
        return abort(400, "invalid 'topic_id' provided")
    new_title = limit_whitespace(data.get("title"))
    new_desc = limit_whitespace(data.get("description"))
    topic = Topic.query.filter_by(id=topic_id).first()
    include = limit_whitespace(data.get("include", "false")).lower() == "true"
    if topic is None:
        return abort(404, f"no topic with id={topic_id} to update")
    if new_title is None and new_desc is None:
        return abort(400, "you must provide 'title' or 'description' to update")

    if new_title is not None and new_title != topic.title:
        topic.title = new_title
    elif new_desc is not None and new_desc != topic.description:
        topic.description = new_desc
    else:
        return jsonify(caution={"message": "you provided same data as in the database and nothing got updated"})

    topic.last_update = datetime.now(pytz.utc).replace(microsecond=0)
    db.session.commit()
    if include:
        return jsonify({"success": f"successfully updated a topic",
                        "topic": topic.to_dict()}), 200
    return jsonify({"success": f"successfully updated a topic", "topic_id": {topic.id}}), 200


@app.route("/topic", methods=["DELETE"])
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


@app.route("/task/search", methods=["GET"])
def search_task():
    search_title = limit_whitespace(request.args.get("title"))
    if not search_title:
        return abort(400, "You must provide 'title' for your search")

    topic_id = limit_whitespace(request.args.get("topic_id"))
    if topic_id is not None:
        try:
            topic_id = int(topic_id)
        except ValueError:
            return abort(400, "invalid 'topic_id' provided")
        results = Task.query.filter_by(topic_id=topic_id).filter(Task.title.like(f"%{search_title}%")).all()
        tasks = {
            "no_of_results": len(results),
            "tasks": [task.to_dict() for task in results]}
        return jsonify(tasks), 200

    results = Task.query.filter(Task.title.like(f"%{search_title}%")).all()
    tasks = {
        "results": len(results),
        "tasks": [task.to_dict() for task in results]
    }
    return jsonify(tasks), 200


@app.route("/topic/<int:topic_id>/task", methods=["GET"])
def all_task(topic_id):
    result = Task.query.filter_by(topic_id=topic_id).all()
    if result is None:
        return abort(404, f"not found tasks associated with topic id={topic_id}")
    response = {
        "num_of_tasks": len(result),
        "tasks": [task.to_dict() for task in result]
    }
    return jsonify(response), 200


@app.route("/topic/<int:topic_id>/task", methods=["POST"])
def add_task(topic_id):
    topic = Topic.query.filter_by(id=topic_id).first()
    if topic is None:
        return abort(
            404,
            f"no topic with id={topic_id} found, you may need to create new topic before creating new task"
        )

    data = request.form.to_dict()
    title = limit_whitespace(data.get("title"))
    due_time = dt_from_string(limit_whitespace(data.get("due_time")))
    status = limit_whitespace(data.get("status", "next"))
    possible_status = ["next", "ongoing", "finished"]
    if status not in possible_status:
        return abort(400, f"invalid status provided can only be one of: {possible_status}")
    status = status.lower()
    include = limit_whitespace(data.get("include", "false")).lower() == "true"
    if title is None or due_time is None:
        return abort(400, "both 'title' and 'due_time' values are needed")

    timestamp = datetime.now(pytz.utc).replace(microsecond=0)
    new_task = Task(
        title=title,
        created_at=timestamp,
        due_time=due_time,
        status=status,
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


@app.route("/topic/<int:topic_id>/task", methods=["PUT"])
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
    new_due_time = dt_from_string(limit_whitespace(data.get("due_time")))
    new_status = limit_whitespace(data.get("status"))
    include = limit_whitespace(data.get("include", "false")).lower() == "true"
    if new_title is None and new_due_time is None and new_status is None:
        return abort(400, "you must provide 'title' or 'due_time' or 'status' to update")
    possible_status = ["next", "ongoing", "finished"]
    if new_status not in possible_status:
        return abort(400, f"invalid status provided can only be one of: {possible_status}")

    if new_status is not None and new_status != task.status:
        task.status = new_status
    elif new_title is not None and new_title != task.title:
        task.title = new_title
    elif new_due_time is not None and new_due_time != task.due_time.replace(tzinfo=pytz.utc):
        task.due_time = new_due_time
    else:
        return jsonify(caution={"code": 204,
                                "message": "you provided same data as in the database and nothing got updated"})

    task.last_update = datetime.now(pytz.utc).replace(microsecond=0)
    db.session.commit()
    if include:
        return jsonify({"success": f"successfully updated a task",
                        "task": task.to_dict()})
    return jsonify({"success": f"successfully updated a task", "task_id": task.id, "topic_id": task.topic.id})


@app.route("/topic/<int:topic_id>/task", methods=["DELETE"])
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


if __name__ == "__main__":
    app.run(debug=debug, port=8080)

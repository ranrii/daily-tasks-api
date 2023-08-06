from flask import Flask, request, abort, jsonify, make_response
import os
from model import db, Topic, Task
from datetime import datetime
from dotenv import load_dotenv # TODO: Remove dotenv dependency before deployment
import pytz
from utils import limit_whitespace

load_dotenv()


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///task.db")
debug = os.environ.get("DEBUG") == "TRUE"
db.init_app(app)
db.create_all()


# TODO: try _asdict(), dict(topic), topic._asdict()

@app.errorhandler(400)
def bad_request(error):
    return jsonify(error={"code": 400, "message": error.description}), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify(error={"code": 404, "message": error.description}), 404


@app.errorhandler(401)
def unauthorized(error):
    return jsonify(error={"code": 401, "message": error.description}), 401


@app.errorhandler(204)
def no_content(error):
    return jsonify(error={"code": 204, "message": error.description}), 204


@app.route("/topic", methods=["GET"])
def all_topic():
    result = Topic.query.all()
    topics = {
        "num_of_topic": len(result),
        "topics": [
            {
                "id": topic.id,
                "title": topic.title,
                "description": topic.description,
                "tasks": [task.title for task in topic.tasks],
                "num_of_tasks": len(topic.tasks)
            } for topic in result]
    }
    return jsonify(topics), 200


@app.route("/topic/search", methods=["GET"])
def search_topic():
    search_query = limit_whitespace(request.args.get("title"))
    result = Topic.query.filter(Topic.title.like(f"%{search_query}%")).all()
    response = {
        "num_of_topic": len(result),
        "topics": [
            {
                "id": topic.id,
                "title": topic.title,
                "description": topic.description,
                "tasks": [task.title for task in topic.tasks],
                "num_of_tasks": len(topic.tasks)
            } for topic in result]
    }
    return jsonify(response), 200


@app.route("/topic", methods=["POST"])
def add_topic():
    timestamp = datetime.now(pytz.utc).replace(microsecond=0).isoformat()
    title = limit_whitespace(request.args.get("title"))
    description = limit_whitespace(request.args.get("description"))
    include = request.args.get("include") == "True"
    if title is None:
        return abort(400, "You must provide 'title' for your new topic")

    new_topic = Topic(
        title=limit_whitespace(title),
        description=limit_whitespace(description),
        created_at=timestamp,
    )
    db.session.add(new_topic)
    db.session.commit()
    if include:
        return jsonify({"success": f"successfully add new topic with id={new_topic.id}",
                        "topic": {"id": new_topic.id,
                                  "title": new_topic.title,
                                  "description": new_topic.description,
                                  "created_at": timestamp},
                        }), 200
    return jsonify({"success": f"successfully add new topic with id={new_topic.id}"}), 200


@app.route("/topic", methods=["PUT"])
def update_topic():
    topic_id = limit_whitespace(request.args.get("topic_id"))
    new_title = limit_whitespace(request.args.get("title"))
    new_desc = request.args.get("description").strip()
    topic = Topic.query.filter_by(id=topic_id).first()
    include = request.args.get("include") == "True"
    if not topic:
        return abort(404, f"no topic with id={topic_id} to update")
    if new_title is None and new_desc is None:
        return abort(400, "you must provide 'title' or 'description' to update")
    if new_title == topic.title and new_desc == topic.description:
        return abort(204, "you provided nothing to update")

    topic.last_update = datetime.now(pytz.utc).replace(microsecond=0).isoformat()
    if new_title is not None:
        topic.title = new_title
    if new_desc is not None:
        topic.description = new_desc
    db.session.commit()
    if include:
        return jsonify({"success": f"successfully updated topic id={topic.id}",
                        "topic": dict(topic)}), 200
    return jsonify({"success": f"successfully updated topic id={topic.id}"}), 200


@app.route("/topic", methods=["DELETE"])
def delete_topic():
    topic_id = request.args.get("topic_id")
    if topic_id is None:
        return abort(400, f"you must provide {topic_id} to remove")

    topic = Topic.query.filter_by(id=topic_id).first()
    if topic is None:
        return abort(404, f"no topic with id={topic_id} found")

    db.session.remove(topic)
    db.session.commit()
    return jsonify({"success": f"successfully removed topic with id={topic.id}"})


@app.route("/task/search", methods=["GET"])
def search_task():
    topic_id = request.args.get("topic_id")
    search_title = limit_whitespace(request.args.get("title"))
    if not search_title:
        return abort(400, "You must provide 'title' for your search")
    if topic_id:
        results = Task.query.filter_by(topic_id=topic_id).filter(Task.title.like(f"%{search_title}%")).all()
        tasks = {
            "results": len(results),
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "created_at": task.created_at,
                    "due_time": task.due_time,
                    "status": task.status,
                    "topic_id": task.topic.id,
                    "topic_name": task.topic.title} for task in results
            ]
        }
        return jsonify(tasks), 200

    results = Task.query.filter_by(title=search_title).all()
    tasks = {
        "results": len(results),
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "created_at": task.created_at,
                "due_time": task.due_time,
                "status": task.status,
                "topic_id": task.topic.id,
                "topic_name": task.topic.title} for task in results
        ]
    }
    if tasks:
        return jsonify(tasks), 200
    return jsonify(error={"code": 404, "message": "not found"}), 404


@app.route("/topic/<int:topic_id>/task", methods=["GET"])
def all_task(topic_id):
    pass


@app.route("/topic/<int:topic_id>/task", methods=["POST"])
def add_task(topic_id):
    pass


@app.route("/topic/<int:topic_id>/task", methods=["PUT"])
def edit_task(topic_id):
    pass


@app.route("/topic/<int:topic_id>/task", methods=["DELETE"])
def delete_task(topic_id):
    pass


if __name__ == "__main__":
    app.run(debug=debug)

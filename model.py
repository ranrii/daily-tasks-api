import pytz
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime
db = SQLAlchemy()

# not implemented
# user_task = db.Table(
#     "user_task",
#     db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
#     db.Column("task_id", db.Integer, db.ForeignKey("task.id"), primary_key=True)
# )
#
# user_topic = db.Table(
#     "user_topic",
#     db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
#     db.Column("topic_id"), db.Integer, db.ForeignKey("topic.id", primary_key=True)
# )


class Topic(db.Model):
    __tablename__ = "topics"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    emoji = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    last_update = db.Column(db.DateTime)
    # relations
    tasks = relationship("Task", back_populates="topic")
    # not implemented
    # user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # users = relationship("User", secondary=user_topic, back_populates="topics")

    def to_dict(self):
        topic_dict = {
            "id": str(self.id),
            "title": self.title,
            "emoji": self.emoji,
            "created_at": datetime.isoformat(self.created_at.replace(tzinfo=pytz.utc)),
            "tasks": [task.to_dict() for task in self.tasks],
            "no_of_tasks": len(self.tasks),
            "editStatus": False,
        }
        if self.last_update is not None:
            topic_dict["last_update"] = datetime.isoformat(self.last_update.replace(tzinfo=pytz.utc))
        return topic_dict


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    detail = db.Column(db.String, nullable=False)
    emoji = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    due_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String, nullable=False)
    last_update = db.Column(db.DateTime)
    # relations
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"))
    topic = relationship("Topic", back_populates="tasks")
    # not implemented
    # users = relationship("User", secondary=user_task, back_populates="tasks")

    def to_dict(self):
        task_dict = {
            "id": str(self.id),
            "title": self.title,
            "detail": self.detail,
            "emoji": self.emoji,
            "created_at": datetime.isoformat(self.created_at.replace(tzinfo=pytz.utc)),
            "due_time": self.due_time_to_date(),
            "status": self.status,
            "topic_title": self.topic.title,
            "topic_id": str(self.topic_id),
            "editStatus": False,
        }
        if self.last_update is not None:
            task_dict["last_update"] = datetime.isoformat(self.last_update.replace(tzinfo=pytz.utc))
        return task_dict

    def due_time_to_date(self):
        due_time = self.due_time.replace(tzinfo=pytz.utc)
        return {"month": due_time.strftime("%b"), "day": due_time.day}


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    last_active = db.Column(db.DateTime, nullable=False)
    login_ip = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    is_block = db.Column(db.Boolean, nullable=False)
#   role = db.Column(db.String, nullable=False)
#     image_url = db.Column(db.String)
#     # relations
#     topics = relationship("Topic", secondary=user_topic, back_populates="users")
#     tasks = relationship("Task", secondary=user_task, back_populates="users")

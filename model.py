from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

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
    description = db.Column(db.String)
    created_at = db.Column(db.DateTime, nullable=False)
    last_update = db.Column(db.DateTime)
    # relations
    tasks = relationship("Task", back_populates="topic")
    # not implemented
    # user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # users = relationship("User", secondary=user_topic, back_populates="topics")


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    due_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String, nullable=False)
    last_update = db.Column(db.DateTime)
    # relations
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"))
    topic = relationship("Topic", back_populates="tasks")
    # not implemented
    # users = relationship("User", secondary=user_task, back_populates="tasks")


# class User(db.Model):  # not implemented
#     __tablename__ = "users"
#     id = db.Column(db.Integerm, primary_key=True)
#     username = db.Column(db.String, unique=True, nullable=False)
#     password = db.Column(db.String, nullable=False)
#     email = db.Column(db.String, nullable=False)
#     created_at = db.Column(db.DateTime, nullable=False)
#     role = db.Column(db.String, nullable=False)
#     image_url = db.Coulum(db.String)
#     # relations
#     topics = relationship("Topic", secondary=user_topic, back_populates="users")
#     tasks = relationship("Task", secondary=user_task, back_populates="users")

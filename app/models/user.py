from datetime import datetime

import pytz
from sqlalchemy.orm import relationship
from app.extensions import db


user_topics = db.Table(
    "user_topics",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("topic_id", db.Integer, db.ForeignKey("topics.id"), primary_key=True)
)

user_tasks = db.Table(
    "user_tasks",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("task_id", db.Integer, db.ForeignKey("tasks.id"), primary_key=True)
)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_block = db.Column(db.Boolean, nullable=False)
    profile = relationship("Profile", uselist=False, back_populates="user")
    topics = relationship("Topic", secondary=user_topics, back_populates="users")
    tasks = relationship("Task", secondary=user_tasks, back_populates="users")


class Profile(db.Model):
    __tablename__ = "profiles"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime(timezone=True), default=datetime.now(pytz.utc))
    last_active = db.Column(db.DateTime(timezone=True), default=datetime.now(pytz.utc), onupdate=datetime.now(pytz.utc))
    login_ip = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = relationship(User.__name__, uselist=False, back_populates="profile")

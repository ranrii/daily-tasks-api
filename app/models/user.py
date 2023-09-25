from datetime import datetime

import pytz
from sqlalchemy.orm import relationship
from app.extensions import db
from utils.connection import get_ip_addr

user_topic = db.Table(
    "user_topics",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("topic_id", db.Integer, db.ForeignKey("topics.id"), primary_key=True),
    db.Column("role", db.String, nullable=False, default="user")
)

user_task = db.Table(
    "user_tasks",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("task_id", db.Integer, db.ForeignKey("tasks.id"), primary_key=True),
    db.Column("role", db.String, nullable=False, default="user")
)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime(timezone=True), default=datetime.now(pytz.utc))
    last_active = db.Column(db.DateTime(timezone=True), default=datetime.now(pytz.utc), onupdate=datetime.now(pytz.utc))
    login_ip = db.Column(db.String, nullable=False, onupdate=get_ip_addr)
    login_at = db.Column(db.DateTime(timezone=True), nullable=True, default=None)
    is_block = db.Column(db.Boolean, nullable=False, default=False)
    role = db.Column(db.String, nullable=False, default="user")
    profile = relationship("Profile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    created_topics = relationship("Topic", back_populates="creator", cascade="all, delete-orphan")
    created_tasks = relationship("Task", back_populates="creator", cascade="all, delete-orphan")
    topics = relationship("Topic", secondary=user_topic, back_populates="users")
    tasks = relationship("Task", secondary=user_task, back_populates="users")

    def to_dict(self):
        user_dict = {
            "id": self.id,
            "username": self.username,
            "account_created": datetime.isoformat(self.created.replace(tzinfo=pytz.utc, microsecond=0)),
            "blocked": self.is_block,
            "profiles": {
                "first_name": self.profile.first_name,
                "last_name": self.profile.last_name
            }
        }
        return user_dict


class Profile(db.Model):
    __tablename__ = "profiles"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = relationship(User.__name__, uselist=False, back_populates="profile")

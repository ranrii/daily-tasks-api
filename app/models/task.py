from datetime import datetime

import pytz
from sqlalchemy.orm import relationship

from app import db


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    detail = db.Column(db.String, nullable=False)
    emoji = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(pytz.utc))
    due_time = db.Column(db.DateTime(timezone=True), nullable=False)
    status = db.Column(db.String, nullable=False)
    last_update = db.Column(db.DateTime(timezone=True), onupdate=datetime.now(pytz.utc), nullable=True)
    # relations
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"))
    topic = relationship("Topic", back_populates="tasks")
    users = relationship("User", secondary="user_tasks", back_populates="tasks")

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

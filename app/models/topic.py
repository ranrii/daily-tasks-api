from sqlalchemy.orm import relationship
from app.extensions import db
from datetime import datetime


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
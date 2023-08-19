import pytz
from sqlalchemy.orm import relationship
from app.extensions import db
from datetime import datetime

from app.models.task import Task


class Topic(db.Model):
    __tablename__ = "topics"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    emoji = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    last_update = db.Column(db.DateTime(timezone=True))
    status = db.Column(db.String, nullable=False)
    num_completed_tasks = db.Column(db.Integer, nullable=False)
    progression = db.Column(db.Integer, nullable=False)
    # relations
    tasks = relationship(Task.__name__, back_populates=Task.topic)
    # not implemented
    # user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # users = relationship("User", secondary=user_topic, back_populates="topics")

    def to_dict(self):
        topic_dict = {
            "id": str(self.id),
            "title": self.title,
            "emoji": self.emoji,
            "status": self.status,
            "progression": self.progression,
            "created_at": datetime.isoformat(self.created_at.replace(tzinfo=pytz.utc)),
            "tasks": [task.to_dict() for task in self.tasks],
            "no_of_tasks": len(self.tasks),
            "editStatus": False,
        }
        if self.last_update is not None:
            topic_dict["last_update"] = datetime.isoformat(self.last_update.replace(tzinfo=pytz.utc))
        return topic_dict

    def progression_calc(self):
        self.count_complete()
        if self.num_completed_tasks == len(self.tasks):
            self.status = "Complete"
            self.progression = 100
        else:
            self.status = "Pending"
            self.progression = int(self.num_completed_tasks/len(self.tasks)*100)

    def count_complete(self):
        self.num_completed_tasks = len([1 for task in self.tasks if task.status == "Complete"])
import pytz
from sqlalchemy.orm import relationship
from app.extensions import db
from datetime import datetime


class Topic(db.Model):
    __tablename__ = "topics"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    emoji = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(pytz.utc))
    last_update = db.Column(db.DateTime(timezone=True), onupdate=datetime.now(pytz.utc), nullable=True)
    status = db.Column(db.String, default="Pending", nullable=False)
    num_completed_tasks = db.Column(db.Integer, default=0, nullable=False)
    progression = db.Column(db.Integer, default=0, nullable=False)
    # relations
    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creator = relationship("User", back_populates="created_topics")
    tasks = relationship("Task", back_populates="topic", cascade="all, delete-orphan")
    users = relationship("User", secondary="user_topics", back_populates="topics")

    def to_dict(self):
        topic_dict = {
            "id": str(self.id),
            "title": self.title,
            "emoji": self.emoji,
            "status": self.status,
            "progression": self.progression,
            "created_at": datetime.isoformat(self.created_at.replace(tzinfo=pytz.utc, microsecond=0)),
            "tasks": [task.to_dict() for task in self.tasks],
            "no_of_tasks": len(self.tasks),
            "editStatus": False,
            "owner": self.creator.username,
            "users": [user.to_dict() for user in self.users]
        }
        if self.last_update is not None:
            topic_dict["last_update"] = datetime.isoformat(self.last_update.replace(tzinfo=pytz.utc, microsecond=0))
        return topic_dict

    def progression_calc(self):
        self.count_complete()
        if len(self.tasks) == 0:
            self.progression = 0
            self.status = "Pending"
        elif self.num_completed_tasks == len(self.tasks):
            self.status = "Complete"
            self.progression = 100
        else:
            self.status = "Pending"
            self.progression = int(self.num_completed_tasks/len(self.tasks)*100)

    def count_complete(self):
        self.num_completed_tasks = len([1 for task in self.tasks if task.status == "Complete"])

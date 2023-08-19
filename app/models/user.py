from app.extensions import db


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
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    is_block = db.Column(db.Boolean, nullable=False)
#   role = db.Column(db.String, nullable=False)
#     image_url = db.Column(db.String)
#     # relations
#     topics = relationship("Topic", secondary=user_topic, back_populates="users")
#     tasks = relationship("Task", secondary=user_task, back_populates="users")

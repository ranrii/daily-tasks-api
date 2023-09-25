from flask import abort
from sqlalchemy import select, and_

from app import db
from app.models.task import Task
from app.models.topic import Topic
from app.models.user import User, user_task, user_topic


POSSIBLE_ROLE = ["user", "creator", "moderator", "topicOwner"]


def check_permission(current_user: User, resources: Topic or Task or list[Topic or Task], role: list):
    if current_user.role == "admin":
        return True

    if type(resources) is not list:
        resources = [resources]

    is_allowed = False
    user_role = None
    resource_names = []
    user_id = current_user.id
    for resource in resources:
        resource_id = resource.id
        resource_name = resource.__tablename__
        resource_names.append(resource_name)

        if resource_name == "tasks":
            cursor = select(user_task.c.role).where(and_(
                user_task.c.task_id == resource_id, user_task.c.user_id == user_id
            ))
        elif resource_name == "topics":
            cursor = select(user_topic.c.role).where(and_(
                    user_topic.c.topic_id == resource_id, user_topic.c.user_id == user_id
            ))
        else:
            raise Exception("unsupported resource")
        user_role = db.session.scalar(cursor)
        if user_role in role or role == ["user"]:
            is_allowed = is_allowed or True

    if user_role is None:
        return abort(403,
                     f"user is not associate with this {' or '.join([text[:-1] for text in resource_names])}")

    if is_allowed:
        return True

    return abort(403, "insufficient role privilege")


def grant_permission(user: User, resources: Topic or Task or list[Topic or Task], role: str):
    if resources is not list:
        resources = [resources]
    if role not in POSSIBLE_ROLE:
        raise Exception("unsupported role")
    for resource in resources:
        if resource.__tablename__ == "topics":
            insert_statement = user_topic.insert().values(user_id=user.id, topic_id=resource.id, role=role)
        elif resource.__tablename__ == "tasks":
            insert_statement = user_task.insert().values(user_id=user.id, task_id=resource.id, role=role)
        else:
            db.session.rollback()
            raise Exception("unsupported resources")

        db.session.execute(insert_statement)

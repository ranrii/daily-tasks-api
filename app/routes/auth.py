
import jwt
from flask import Blueprint, request, jsonify, abort, current_app
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models.user import User, Profile
from app.routes import issue_token, verify_token
from utils.connection import get_ip_addr
from utils.mail_service import send_mail, check_email
from smtplib import SMTPException
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.form.to_dict()
    if None in [data.get("email"), data.get("password")]:
        return abort(401, "invalid login details")
    email = check_email(data.get("email"))
    user = db.session.execute(db.select(User).where(User.email == email)).scalar()
    if user is None:
        return abort(404, "user not found")
    password = data.get("password")
    if not check_password_hash(user.password, password):
        return abort(403, "Invalid login details")

    return jsonify({"user": {"id": user.id, "username": user.username}, "token": issue_token(user, 3600)}), 200


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.form.to_dict()
    if None in [data.get("username"),
                data.get("first_name"),
                data.get("last_name"),
                data.get("password"),
                data.get("email")]:
        return abort(400, "missing required data")
    email = check_email(data.get("email"))
    if db.session.execute(db.select(User).where(User.email == email)).one_or_none() is not None:
        return abort(400, "user has already registered")

    user = User()
    user_profile = Profile(user=user)
    user.username = data.get("username")
    user.password = generate_password_hash(data.get("password"), method="pbkdf2", salt_length=10)
    user.login_ip = get_ip_addr()
    user_profile.first_name = data.get("first_name")
    user_profile.last_name = data.get("last_name")
    user.email = email
    db.session.add(user)
    db.session.add(user_profile)
    db.session.commit()
    return jsonify({"user": {"id": user.id, "username": user.username}, "token": issue_token(user, 3600)}), 200


@auth_bp.route("/refresh", methods=["GET"])
def refresh_token():
    if "token" not in request.headers:
        return abort(401, "no token provided")
    old_token = request.headers.get("token")
    decoded = jwt.decode(
        old_token,
        key=current_app.secret_key,
        algorithms="HS256",
        options={"require": ["sub", "aud", "iat"]}
    )
    if "sub" not in decoded or "aud" not in decoded or "iat" not in decoded:
        return abort(401, "invalid token")
    user = db.session.execute(
        db.select(User).where(User.id == decoded["sub"] and User.username == decoded["aud"])).one_or_none()
    if user is None:
        return abort(401, "no user associated with this token")
    current_ip = get_ip_addr()
    if current_ip != user.login_ip:
        return abort(401, "user location changed, please login again")
    return jsonify({"token": issue_token(user, 3600)}), 200


# WIP or not implemented BELOW ⤵
# noinspection PyUnreachableCode
@auth_bp.route("/forget", methods=["POST"])
def forgor():
    return jsonify(error="not implemented") # remove this before implementing User

    data = request.form.to_dict()
    email = check_email(data.get("email"))
    url = data.get("url")
    if None in [email, url]:
        return abort(401, "missing required data")
    user = db.session.execute(db.select(User).where(User.email == data["email"])).one_or_none()
    if user is None:
        return abort(404, "user not found")
    token = issue_token(user, 180)
    reset_url = f"<insert-url-to-reset-password-page-here>?reset-key={token}"
    try:
        send_mail(user, reset_url)
    except SMTPException as e:
        return jsonify(
            error={"code": 424, "message": "an error occurred while try sending mail", "reasons": str(e)}), 424


# noinspection PyUnreachableCode
@auth_bp.route("/reset", methods=["POST"])
def reset_password():
    return jsonify(error="not implemented") # remove this before implementing User

    token = request.args.get("reset-key")
    if not verify_token(token):
        return abort(401, "unauthorized")
    decoded = jwt.decode(token, key=current_app.secret_key, algorithms="HS256")
    data = request.form.to_dict()
    if "password" not in data:
        return abort(400, "new password is required")
    user = db.session.execute(
        db.select(User).where(User.id == decoded["sub"] and User.email == decoded["aud"])).one_or_none()
    if user is None:
        return abort(404, "user not found")
    user.password = generate_password_hash(data.get("password"), method="pbkdf2", salt_length=10)
    db.session.commit()
    return jsonify({"success": "successfully changed the password"}), 200

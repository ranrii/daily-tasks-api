from flask import Blueprint, jsonify

error_bp = Blueprint("error", __name__)


@error_bp.app_errorhandler(400)
def bad_request(error):
    return jsonify(error={"code": 400, "message": error.description}), 400


@error_bp.app_errorhandler(404)
def not_found(error):
    return jsonify(error={"code": 404, "message": error.description}), 404


@error_bp.app_errorhandler(401)
def unauthorized(error):
    return jsonify(error={"code": 401, "message": error.description}), 401


@error_bp.app_errorhandler(415)
def unsupported(error):
    return jsonify(error={"code": 415, "message": "please format your data in the dictionary-typed/json format"}), 415


@error_bp.app_errorhandler(500)
def generic_error(error):
    return jsonify(error={"message": "bug alert, check the logs"}), 500

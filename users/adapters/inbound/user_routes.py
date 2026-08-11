from flask import Blueprint, jsonify

user_blueprint = Blueprint("user", __name__)

@user_blueprint.route("/api/users", methods=["GET"])
def list_users():
    return jsonify([])

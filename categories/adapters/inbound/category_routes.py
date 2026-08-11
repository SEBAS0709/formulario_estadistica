from flask import Blueprint, jsonify

category_blueprint = Blueprint("category", __name__)

@category_blueprint.route("/api/categories", methods=["GET"])
def list_categories():
    return jsonify([])

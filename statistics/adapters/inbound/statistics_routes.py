from flask import Blueprint, jsonify

statistics_blueprint = Blueprint("statistics", __name__)

@statistics_blueprint.route("/api/statistics", methods=["GET"])
def statistics_info():
    return jsonify({"total_calculations": 0, "top_formula": None})

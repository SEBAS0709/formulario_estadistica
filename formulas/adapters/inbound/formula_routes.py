import json
from flask import Blueprint, jsonify, request
from formulas.adapters.outbound.sqlalchemy_models import Formula
from statistics.adapters.outbound.sqlalchemy_models import CalculationHistory
from formulas.application.calculator import Calculator
from shared.adapters.outbound.database import db
from shared.adapters.inbound.auth import login_required, admin_required

formula_blueprint = Blueprint("formula", __name__)


def serialize_formula(formula):
    return {
        "id": formula.id,
        "name": formula.name,
        "category": formula.category,
        "expression": formula.expression,
        "description": formula.description,
        "purpose": formula.purpose,
        "variables": json.loads(formula.variables),
        "inputs": json.loads(formula.inputs),
        "example": formula.example,
        "favorite": formula.favorite,
    }


@formula_blueprint.route("/api/formulas", methods=["GET"])
def list_formulas():
    formulas = Formula.query.order_by(Formula.category, Formula.name).all()
    return jsonify([serialize_formula(formula) for formula in formulas])


# Admin: create, update, delete formulas
@formula_blueprint.route("/admin/formulas", methods=["POST"])
@admin_required
def create_formula():
    payload = request.json or {}
    name = payload.get("name")
    if not name:
        return jsonify({"error": "name required"}), 400
    existing = Formula.query.filter_by(name=name).first()
    if existing:
        return jsonify({"error": "already exists"}), 400
    formula = Formula(
        name=name,
        category=payload.get("category", "General"),
        expression=payload.get("expression", ""),
        description=payload.get("description", ""),
        purpose=payload.get("purpose", ""),
        variables=json.dumps(payload.get("variables", [])),
        inputs=json.dumps(payload.get("inputs", [])),
        example=payload.get("example", ""),
    )
    db.session.add(formula)
    db.session.commit()
    return jsonify(serialize_formula(formula)), 201


@formula_blueprint.route("/admin/formulas/<int:fid>", methods=["PUT"])
@admin_required
def update_formula(fid):
    formula = Formula.query.get_or_404(fid)
    payload = request.json or {}
    for key in ("name", "category", "expression", "description", "purpose", "example"):
        if key in payload:
            setattr(formula, key, payload[key])
    if "variables" in payload:
        formula.variables = json.dumps(payload["variables"])
    if "inputs" in payload:
        formula.inputs = json.dumps(payload["inputs"])
    db.session.commit()
    return jsonify(serialize_formula(formula))


@formula_blueprint.route("/admin/formulas/<int:fid>", methods=["DELETE"])
@admin_required
def delete_formula(fid):
    formula = Formula.query.get_or_404(fid)
    db.session.delete(formula)
    db.session.commit()
    return jsonify({"deleted": True})


@formula_blueprint.route("/api/calculations", methods=["POST"])
def calculate_formula():
    payload = request.json or {}
    formula_id = payload.get("formula_id")
    formula_name = payload.get("formula_name")

    formula = None
    if formula_id is not None:
        formula = Formula.query.get(formula_id)
    if formula is None and formula_name:
        formula = Formula.query.filter_by(name=formula_name).first()
    if formula is None:
        return jsonify({"error": "Fórmula no encontrada"}), 404

    values = payload.get("values")
    parameters = payload.get("parameters") or {}
    parsed_values = Calculator.parse_values(values)
    result, steps = Calculator.calculate(formula.name, parsed_values, parameters)

    # include user info in input_data so history can be filtered per user without schema changes
    user_info = {}
    try:
        from flask import session
        if session.get("user_id"):
            user_info = {"user_id": session.get("user_id"), "username": session.get("username")}
    except Exception:
        user_info = {}

    full_input = {"payload": payload, "user": user_info}

    history_entry = CalculationHistory(
        formula_name=formula.name,
        input_data=json.dumps(full_input),
        result=str(result),
    )
    db.session.add(history_entry)
    db.session.commit()

    return jsonify({
        "formula_id": formula.id,
        "formula_name": formula.name,
        "input_data": json.dumps(full_input),
        "result": result,
        "steps": steps,
    })


# Favorites endpoints
@formula_blueprint.route("/api/favorites", methods=["GET"])
@login_required
def list_favorites():
    from users.adapters.outbound.sqlalchemy_models import Favorite
    from flask import session
    user_id = session.get("user_id")
    favs = Favorite.query.filter_by(user_id=user_id).all()
    return jsonify([f.to_dict() for f in favs])


@formula_blueprint.route("/api/favorites", methods=["POST"])
@login_required
def add_favorite():
    from users.adapters.outbound.sqlalchemy_models import Favorite
    from flask import session
    payload = request.json or {}
    formula_id = payload.get("formula_id")
    if not formula_id:
        return jsonify({"error": "formula_id required"}), 400
    user_id = session.get("user_id")
    existing = Favorite.query.filter_by(user_id=user_id, formula_id=formula_id).first()
    if existing:
        return jsonify({"error": "already favorited"}), 400
    fav = Favorite(user_id=user_id, formula_id=formula_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.to_dict()), 201


@formula_blueprint.route("/api/favorites/<int:fid>", methods=["DELETE"])
@login_required
def remove_favorite(fid):
    from users.adapters.outbound.sqlalchemy_models import Favorite
    from flask import session
    user_id = session.get("user_id")
    fav = Favorite.query.get_or_404(fid)
    if fav.user_id != user_id and session.get("role") != "admin":
        return jsonify({"error": "not allowed"}), 403
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"deleted": True})


# History endpoints (filter by session user)
@formula_blueprint.route("/api/history", methods=["GET"])
@login_required
def user_history():
    from flask import session
    user_id = session.get("user_id")
    entries = CalculationHistory.query.order_by(CalculationHistory.created_at.desc()).all()
    res = []
    for e in entries:
        try:
            d = json.loads(e.input_data)
            if d.get("user", {}).get("user_id") == user_id:
                res.append(e.to_dict())
        except Exception:
            continue
    return jsonify(res)

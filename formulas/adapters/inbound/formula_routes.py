import json
from flask import Blueprint, jsonify, request
from formulas.adapters.outbound.sqlalchemy_models import Formula
from statistics.adapters.outbound.sqlalchemy_models import CalculationHistory
from formulas.application.calculator import Calculator
from shared.adapters.outbound.database import db

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

@formula_blueprint.route("/api/calculations", methods=["POST"])
def calculate_formula():
    payload = request.json or {}
    formula_id = payload.get("formula_id")
    formula = Formula.query.get(formula_id)
    if formula is None:
        return jsonify({"error": "Fórmula no encontrada"}), 404

    values = payload.get("values")
    parsed_values = Calculator.parse_values(values)
    result, steps = Calculator.calculate(formula_id, parsed_values)

    history_entry = CalculationHistory(
        formula_name=formula.name,
        input_data=json.dumps(payload),
        result=str(result),
    )
    db.session.add(history_entry)
    db.session.commit()

    return jsonify({
        "formula_id": formula_id,
        "formula_name": formula.name,
        "input_data": json.dumps(payload),
        "result": str(result),
        "steps": steps,
    })

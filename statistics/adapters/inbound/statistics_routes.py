from flask import Blueprint, jsonify
from statistics.adapters.outbound.sqlalchemy_models import CalculationHistory
from formulas.adapters.outbound.sqlalchemy_models import Formula
from shared.adapters.outbound.database import db
from sqlalchemy import func

statistics_blueprint = Blueprint("statistics", __name__)


@statistics_blueprint.route("/api/statistics", methods=["GET"])
def statistics_info():
    total = db.session.query(func.count(CalculationHistory.id)).scalar() or 0

    top = (
        db.session.query(CalculationHistory.formula_name, func.count(CalculationHistory.id).label("cnt"))
        .group_by(CalculationHistory.formula_name)
        .order_by(func.count(CalculationHistory.id).desc())
        .first()
    )
    top_formula = top[0] if top else None

    by_category = (
        db.session.query(Formula.category, func.count(CalculationHistory.id).label("cnt"))
        .join(Formula, Formula.name == CalculationHistory.formula_name)
        .group_by(Formula.category)
        .order_by(func.count(CalculationHistory.id).desc())
        .all()
    )
    categories = [{"category": c[0], "count": c[1]} for c in by_category]

    return jsonify({"total_calculations": total, "top_formula": top_formula, "by_category": categories})


@statistics_blueprint.route("/api/calculations_by_day", methods=["GET"])
def calculations_by_day():
    rows = (
        db.session.query(func.date(CalculationHistory.created_at).label("date"), func.count(CalculationHistory.id))
        .group_by(func.date(CalculationHistory.created_at))
        .order_by(func.date(CalculationHistory.created_at))
        .all()
    )
    return jsonify([{"date": r[0].isoformat(), "count": r[1]} for r in rows])

from flask import Blueprint, jsonify, request
from categories.adapters.outbound.sqlalchemy_models import Category
from shared.adapters.outbound.database import db
from shared.adapters.inbound.auth import admin_required

category_blueprint = Blueprint("category", __name__)


@category_blueprint.route("/api/categories", methods=["GET"])
def list_categories():
    cats = Category.query.order_by(Category.name).all()
    return jsonify([c.to_dict() for c in cats])


@category_blueprint.route("/admin/categories", methods=["POST"])
@admin_required
def create_category():
    payload = request.json or {}
    name = payload.get("name")
    description = payload.get("description", "")
    if not name:
        return jsonify({"error": "name required"}), 400
    existing = Category.query.filter_by(name=name).first()
    if existing:
        return jsonify({"error": "already exists"}), 400
    cat = Category(name=name, description=description)
    db.session.add(cat)
    db.session.commit()
    return jsonify(cat.to_dict()), 201


@category_blueprint.route("/admin/categories/<int:cat_id>", methods=["PUT"])
@admin_required
def update_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    payload = request.json or {}
    cat.name = payload.get("name", cat.name)
    cat.description = payload.get("description", cat.description)
    db.session.commit()
    return jsonify(cat.to_dict())


@category_blueprint.route("/admin/categories/<int:cat_id>", methods=["DELETE"])
@admin_required
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    return jsonify({"deleted": True})

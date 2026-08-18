from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from shared.adapters.outbound.database import db
from users.adapters.outbound.sqlalchemy_models import User
from shared.adapters.inbound.auth import admin_required

user_blueprint = Blueprint("user", __name__)


@user_blueprint.route("/register", methods=["GET"]) 
def register_form():
    return render_template("register.html")


@user_blueprint.route("/register", methods=["POST"]) 
def register():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    password2 = request.form.get("password2", "")

    if not username or not password:
        flash("Username and password are required.", "error")
        return redirect(url_for("user.register_form"))
    if password != password2:
        flash("Passwords do not match.", "error")
        return redirect(url_for("user.register_form"))

    with db.session.no_autoflush:
        existing = User.query.filter_by(username=username).first()
        if existing:
            flash("Username already exists.", "error")
            return redirect(url_for("user.register_form"))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

    session["user_id"] = user.id
    session["username"] = user.username
    session["role"] = user.role
    flash("Registered and logged in.", "success")
    return redirect(url_for("home"))


@user_blueprint.route("/login", methods=["GET"]) 
def login_form():
    return render_template("login.html")


@user_blueprint.route("/login", methods=["POST"]) 
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        flash("Invalid credentials.", "error")
        return redirect(url_for("user.login_form"))

    session["user_id"] = user.id
    session["username"] = user.username
    session["role"] = user.role
    flash("Logged in.", "success")
    return redirect(url_for("home"))


@user_blueprint.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("role", None)
    flash("Logged out.", "success")
    return redirect(url_for("home"))


@user_blueprint.route("/api/users", methods=["GET"]) 
def list_users():
    users = User.query.all()
    return {"users": [u.to_dict() for u in users]}


# Admin management
@user_blueprint.route("/admin/users", methods=["GET"])
@admin_required
def admin_list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return {"users": [u.to_dict() for u in users]}


@user_blueprint.route("/admin/users/<int:uid>/role", methods=["PUT"])
@admin_required
def change_role(uid):
    payload = request.json or {}
    role = payload.get("role")
    if role not in ("user", "admin"):
        return {"error": "invalid role"}, 400
    user = User.query.get_or_404(uid)
    user.role = role
    db.session.commit()
    return user.to_dict()


@user_blueprint.route("/admin/users/<int:uid>", methods=["DELETE"])
@admin_required
def delete_user(uid):
    user = User.query.get_or_404(uid)
    db.session.delete(user)
    db.session.commit()
    return {"deleted": True}

from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Se requiere iniciar sesión.", "error")
            return redirect(url_for("user.login_form"))
        return f(*args, **kwargs)

    return wrapped


def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Acceso denegado. Administrador requerido.", "error")
            return redirect(url_for("home"))
        return f(*args, **kwargs)

    return wrapped

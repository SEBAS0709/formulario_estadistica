from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    db.init_app(app)
    with app.app_context():
        from users.adapters.outbound.sqlalchemy_models import User
        from categories.adapters.outbound.sqlalchemy_models import Category
        from formulas.adapters.outbound.sqlalchemy_models import Formula
        from statistics.adapters.outbound.sqlalchemy_models import CalculationHistory
        db.create_all()

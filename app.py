import os
from flask import Flask, render_template
from shared.adapters.outbound.database import init_db, db
from users.adapters.inbound.user_routes import user_blueprint
from formulas.adapters.inbound.formula_routes import formula_blueprint
from formulas.adapters.outbound.sqlalchemy_models import Formula as FormulaModel
from categories.adapters.inbound.category_routes import category_blueprint
from categories.adapters.outbound.sqlalchemy_models import Category as CategoryModel
from statistics.adapters.inbound.statistics_routes import statistics_blueprint

instance_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "instance")
os.makedirs(instance_path, exist_ok=True)
app = Flask(__name__, instance_path=instance_path, template_folder="templates", static_folder="static")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(instance_path, 'statformula.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "dev-secret"

init_db(app)

FORMULA_SEED = [
    {
        "name": "Media Aritmética",
        "category": "Tendencia Central",
        "expression": "x̄ = Σx / n",
        "description": "Calcula la media de un conjunto de valores.",
        "purpose": "Obtener el promedio de un conjunto de datos.",
        "variables": "[{\"name\": \"Valores\", \"description\": \"Lista de valores numérricos.\"}]",
        "inputs": "[{\"name\": \"values\", \"label\": \"Valores (separados por comas)\", \"type\": \"text\"}]",
        "example": "20, 25, 30"
    },
    {
        "name": "Mediana",
        "category": "Tendencia Central",
        "expression": "Mediana = valor medio",
        "description": "Encuentra el valor central en un conjunto ordenado.",
        "purpose": "Identificar el valor que separa los datos en dos grupos iguales.",
        "variables": "[{\"name\": \"Valores\", \"description\": \"Lista de valores numéricos.\"}]",
        "inputs": "[{\"name\": \"values\", \"label\": \"Valores (separados por comas)\", \"type\": \"text\"}]",
        "example": "15, 20, 25, 30, 35"
    },
    {
        "name": "Moda",
        "category": "Tendencia Central",
        "expression": "Moda = valor con mayor frecuencia",
        "description": "Encuentra el valor que aparece con mayor frecuencia.",
        "purpose": "Identificar el valor más común en los datos.",
        "variables": "[{\"name\": \"Valores\", \"description\": \"Lista de valores numéricos.\"}]",
        "inputs": "[{\"name\": \"values\", \"label\": \"Valores (separados por comas)\", \"type\": \"text\"}]",
        "example": "1, 2, 2, 3, 4"
    },
]

CATEGORY_SEED = [
    {"name": "Tendencia Central", "description": "Fórmulas para encontrar medidas centrales"},
    {"name": "Medidas de Dispersión", "description": "Fórmulas que definen la variabilidad de los datos"},
    {"name": "Medidas de Posición", "description": "Fórmulas para ubicar datos en percentiles y cuartiles"},
]


def seed_database():
    with app.app_context():
        if not CategoryModel.query.first():
            for category in CATEGORY_SEED:
                db.session.add(CategoryModel(**category))
        if not FormulaModel.query.first():
            for formula in FORMULA_SEED:
                db.session.add(FormulaModel(**formula))
        db.session.commit()

seed_database()

app.register_blueprint(user_blueprint)
app.register_blueprint(formula_blueprint)
app.register_blueprint(statistics_blueprint)
app.register_blueprint(category_blueprint)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

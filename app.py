import json
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
        "variables": json.dumps([{"name": "Valores", "description": "Lista de valores numéricos."}]),
        "inputs": json.dumps([{"name": "values", "label": "Valores", "type": "text"}]),
        "example": "10, 20, 30, 40",
    },
    {
        "name": "Mediana",
        "category": "Tendencia Central",
        "expression": "Mediana = valor medio",
        "description": "Encuentra el valor central en un conjunto ordenado.",
        "purpose": "Identificar el valor que separa los datos en dos grupos iguales.",
        "variables": json.dumps([{"name": "Valores", "description": "Lista de valores numéricos."}]),
        "inputs": json.dumps([{"name": "values", "label": "Valores", "type": "text"}]),
        "example": "15, 20, 25, 30, 35",
    },
    {
        "name": "Moda",
        "category": "Tendencia Central",
        "expression": "Moda = valor con mayor frecuencia",
        "description": "Encuentra el valor que aparece con mayor frecuencia.",
        "purpose": "Identificar el valor más común en los datos.",
        "variables": json.dumps([{"name": "Valores", "description": "Lista de valores numéricos."}]),
        "inputs": json.dumps([{"name": "values", "label": "Valores", "type": "text"}]),
        "example": "1, 2, 2, 3, 4",
    },
    {
        "name": "Desviación respecto de la media",
        "category": "Medidas de Dispersión",
        "expression": "d_i = x_i - x̄",
        "description": "Calcula la diferencia entre cada valor y la media.",
        "purpose": "Medir cada desviación individual respecto a la media.",
        "variables": json.dumps([{"name": "Valores", "description": "Lista de valores numéricos."}]),
        "inputs": json.dumps([{"name": "values", "label": "Valores", "type": "text"}]),
        "example": "2, 4, 6, 8",
    },
    {
        "name": "Desviación media",
        "category": "Medidas de Dispersión",
        "expression": "MD = Σ|x_i - x̄| / n",
        "description": "Calcula la desviación media promedio respecto a la media.",
        "purpose": "Evaluar la dispersión promedio de los datos.",
        "variables": json.dumps([{"name": "Valores", "description": "Lista de valores numéricos."}]),
        "inputs": json.dumps([{"name": "values", "label": "Valores", "type": "text"}]),
        "example": "2, 4, 6, 8",
    },
    {
        "name": "Varianza poblacional",
        "category": "Medidas de Dispersión",
        "expression": "σ² = Σ(x_i - μ)² / N",
        "description": "Calcula la varianza de un conjunto completo de datos.",
        "purpose": "Medir la dispersión con respecto a la media poblacional.",
        "variables": json.dumps([{"name": "Valores", "description": "Lista de valores numéricos."}]),
        "inputs": json.dumps([{"name": "values", "label": "Valores", "type": "text"}]),
        "example": "2, 4, 6, 8",
    },
    {
        "name": "Desviación estándar poblacional",
        "category": "Medidas de Dispersión",
        "expression": "σ = √σ²",
        "description": "Calcula la desviación estándar de la población.",
        "purpose": "Medir la dispersión en la misma unidad que los datos.",
        "variables": json.dumps([{"name": "Valores", "description": "Lista de valores numéricos."}]),
        "inputs": json.dumps([{"name": "values", "label": "Valores", "type": "text"}]),
        "example": "2, 4, 6, 8",
    },
    {
        "name": "Cuartiles",
        "category": "Medidas de Posición",
        "expression": "Q1, Q2, Q3 = valores de posición",
        "description": "Divide los datos en cuatro partes iguales.",
        "purpose": "Ubicar los cuartiles de una distribución.",
        "variables": json.dumps([{"name": "Valores", "description": "Lista de valores numéricos."}]),
        "inputs": json.dumps([{"name": "values", "label": "Valores", "type": "text"}]),
        "example": "10, 20, 30, 40, 50, 60, 70",
    },
    {
        "name": "Deciles",
        "category": "Medidas de Posición",
        "expression": "D1...D9 = valores de posición",
        "description": "Divide los datos en diez partes iguales.",
        "purpose": "Ubicar posiciones en deciles.",
        "variables": json.dumps([{"name": "Valores", "description": "Lista de valores numéricos."}]),
        "inputs": json.dumps([{"name": "values", "label": "Valores", "type": "text"}]),
        "example": "10, 20, 30, 40, 50, 60, 70, 80, 90",
    },
    {
        "name": "Percentiles",
        "category": "Medidas de Posición",
        "expression": "P_k = valor de posición",
        "description": "Calcula el percentil de un conjunto de datos.",
        "purpose": "Determinar el valor en una posición específica.",
        "variables": json.dumps([{"name": "Valores", "description": "Lista de valores numéricos."}]),
        "inputs": json.dumps([{"name": "values", "label": "Valores", "type": "text"}]),
        "example": "10, 20, 30, 40, 50",
    },
    {
        "name": "Probabilidad simple",
        "category": "Probabilidad",
        "expression": "P(A) = favorable / total",
        "description": "Calcula la probabilidad clásica de un evento.",
        "purpose": "Determinar la probabilidad de un suceso favorable.",
        "variables": json.dumps([{"name": "Favorable", "description": "Cantidad de resultados favorables."}, {"name": "Total", "description": "Cantidad total de resultados."}]),
        "inputs": json.dumps([{"name": "values", "label": "Favorable / Total", "type": "text"}]),
        "example": "3, 10",
    },
    {
        "name": "Complementaria",
        "category": "Probabilidad",
        "expression": "P(A^c) = 1 - P(A)",
        "description": "Calcula la probabilidad del evento complementario.",
        "purpose": "Estimar la probabilidad contraria a un suceso.",
        "variables": json.dumps([{"name": "P(A)", "description": "Probabilidad del evento."}]),
        "inputs": json.dumps([{"name": "values", "label": "P(A)", "type": "text"}]),
        "example": "0.7",
    },
    {
        "name": "Regla de la suma",
        "category": "Probabilidad",
        "expression": "P(A∪B) = P(A) + P(B) - P(A∩B)",
        "description": "Calcula la probabilidad de la unión de dos eventos.",
        "purpose": "Resolver uniones de eventos con solapamiento.",
        "variables": json.dumps([{"name": "P(A)", "description": "Probabilidad del evento A."}, {"name": "P(B)", "description": "Probabilidad del evento B."}, {"name": "P(A∩B)", "description": "Probabilidad de la intersección."}]),
        "inputs": json.dumps([{"name": "values", "label": "P(A), P(B), P(A∩B)", "type": "text"}]),
        "example": "0.3, 0.5, 0.2",
    },
    {
        "name": "Probabilidad condicional",
        "category": "Probabilidad",
        "expression": "P(A|B) = P(A∩B) / P(B)",
        "description": "Calcula la probabilidad condicional de A dado B.",
        "purpose": "Determinar la probabilidad de un evento condicionado.",
        "variables": json.dumps([{"name": "P(A∩B)", "description": "Probabilidad de la intersección."}, {"name": "P(B)", "description": "Probabilidad del evento B."}]),
        "inputs": json.dumps([{"name": "values", "label": "P(A∩B), P(B)", "type": "text"}]),
        "example": "0.2, 0.5",
    },
    {
        "name": "Regla del producto",
        "category": "Probabilidad",
        "expression": "P(A∩B) = P(A) × P(B|A)",
        "description": "Calcula la probabilidad de la intersección de dos eventos.",
        "purpose": "Resolver productos de probabilidades condicionales.",
        "variables": json.dumps([{"name": "P(A)", "description": "Probabilidad del evento A."}, {"name": "P(B|A)", "description": "Probabilidad condicional."}]),
        "inputs": json.dumps([{"name": "values", "label": "P(A), P(B|A)", "type": "text"}]),
        "example": "0.4, 0.7",
    },
    {
        "name": "Distribución binomial",
        "category": "Distribución Binomial",
        "expression": "P(X=x)=C(n,x)p^x(1-p)^(n-x)",
        "description": "Calcula probabilidades para una distribución binomial.",
        "purpose": "Modelar ensayos con éxito o fracaso.",
        "variables": json.dumps([{"name": "n", "description": "Número de ensayos."}, {"name": "x", "description": "Número de éxitos."}, {"name": "p", "description": "Probabilidad de éxito."}]),
        "inputs": json.dumps([{"name": "values", "label": "n, x, p", "type": "text"}]),
        "example": "4, 2, 0.5",
    },
]

CATEGORY_SEED = [
    {"name": "Tendencia Central", "description": "Fórmulas para encontrar medidas centrales"},
    {"name": "Medidas de Dispersión", "description": "Fórmulas que definen la variabilidad de los datos"},
    {"name": "Medidas de Posición", "description": "Fórmulas para ubicar datos en percentiles y cuartiles"},
    {"name": "Probabilidad", "description": "Fórmulas básicas de probabilidad"},
    {"name": "Distribución Binomial", "description": "Fórmulas para distribuciones binomiales"},
]


def seed_database():
    with app.app_context():
        for category in CATEGORY_SEED:
            existing = CategoryModel.query.filter_by(name=category["name"]).first()
            if existing:
                existing.description = category["description"]
            else:
                db.session.add(CategoryModel(**category))
        for formula in FORMULA_SEED:
            existing = FormulaModel.query.filter_by(name=formula["name"]).first()
            if existing:
                for key, value in formula.items():
                    if key != "name":
                        setattr(existing, key, value)
            else:
                db.session.add(FormulaModel(**formula))

        # Crear usuario administrador por defecto si no existe (desarrollo local)
        try:
            from users.adapters.outbound.sqlalchemy_models import User as UserModel
            admin = UserModel.query.filter_by(username="admin").first()
            if not admin:
                admin = UserModel(username="admin", role="admin")
                admin.set_password("admin")
                db.session.add(admin)
        except Exception:
            # Si no existe el módulo User aún, omitir (se crearán tablas luego)
            pass

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

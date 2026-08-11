import json
from math import comb, sqrt


class CalculationResult:
    def __init__(self, formula_id, formula_name, result, steps, input_data):
        self.formula_id = formula_id
        self.formula_name = formula_name
        self.result = result
        self.steps = steps
        self.input_data = input_data

    def to_dict(self):
        return {
            "formula_id": self.formula_id,
            "formula_name": self.formula_name,
            "result": self.result,
            "steps": self.steps,
            "input_data": self.input_data,
        }


class Calculator:
    @staticmethod
    def parse_values(values):
        if values is None:
            return []
        if isinstance(values, str):
            text = values.strip()
            if text.startswith("[") or text.startswith("{"):
                try:
                    parsed = json.loads(text)
                    if isinstance(parsed, list):
                        return [float(value) for value in parsed]
                    if isinstance(parsed, dict) and isinstance(parsed.get("values"), list):
                        return [float(value) for value in parsed["values"]]
                except (json.JSONDecodeError, TypeError, ValueError):
                    pass
            return [float(value.strip()) for value in text.split(",") if value.strip()]
        if isinstance(values, list):
            return [float(value) for value in values if value not in [None, ""]]
        if isinstance(values, dict):
            return [float(value) for value in values.get("values", []) if value not in [None, ""]]
        return []

    @staticmethod
    def arithmetic_mean(values):
        total = sum(values)
        count = len(values)
        result = total / count if count else 0
        steps = [f"Valores: {values}", f"Suma: {total}", f"Cantidad: {count}", f"Media = {total} / {count} = {result}"]
        return result, steps

    @staticmethod
    def median(values):
        ordered = sorted(values)
        count = len(ordered)
        if count == 0:
            result = 0
        elif count % 2 == 1:
            result = ordered[count // 2]
        else:
            result = (ordered[count // 2 - 1] + ordered[count // 2]) / 2
        steps = [f"Valores ordenados: {ordered}", f"Mediana = {result}"]
        return result, steps

    @staticmethod
    def mode(values):
        frequency = {}
        for value in values:
            frequency[value] = frequency.get(value, 0) + 1
        max_freq = max(frequency.values()) if frequency else 0
        modes = [value for value, freq in frequency.items() if freq == max_freq]
        result = modes if len(modes) > 1 else modes[0] if modes else None
        steps = [f"Frecuencias: {frequency}", f"Moda = {result}"]
        return result, steps

    @staticmethod
    def deviation_from_mean(values):
        if not values:
            return [], ["No hay datos para calcular desviaciones."]
        mean = Calculator.arithmetic_mean(values)[0]
        deviations = [value - mean for value in values]
        steps = [f"Media = {mean}", f"Desviaciones: {deviations}"]
        return deviations, steps

    @staticmethod
    def mean_deviation(values):
        if not values:
            return 0, ["No hay datos para calcular la desviación media."]
        mean = Calculator.arithmetic_mean(values)[0]
        absolute_deviations = [abs(value - mean) for value in values]
        result = sum(absolute_deviations) / len(values)
        steps = [f"Media = {mean}", f"Desviaciones absolutas: {absolute_deviations}", f"MD = Σ|x - x̄| / n = {result}"]
        return result, steps

    @staticmethod
    def population_variance(values):
        if not values:
            return 0, ["No hay datos para calcular la varianza."]
        mean = Calculator.arithmetic_mean(values)[0]
        squared_differences = [(value - mean) ** 2 for value in values]
        result = sum(squared_differences) / len(values)
        steps = [f"Media = {mean}", f"Diferencias al cuadrado: {squared_differences}", f"Varianza = Σ(x - μ)^2 / N = {result}"]
        return result, steps

    @staticmethod
    def population_std_dev(values):
        variance, steps = Calculator.population_variance(values)
        result = sqrt(variance)
        steps.append(f"Desviación estándar = √{variance} = {result}")
        return result, steps

    @staticmethod
    def quantile(values, q):
        if not values:
            return 0
        ordered = sorted(values)
        position = (len(ordered) - 1) * q
        lower = int(position)
        upper = min(lower + 1, len(ordered) - 1)
        if lower == upper:
            return ordered[lower]
        fraction = position - lower
        return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction

    @staticmethod
    def quartiles(values):
        result = [Calculator.quantile(values, 0.25), Calculator.quantile(values, 0.5), Calculator.quantile(values, 0.75)]
        steps = [f"Valores ordenados: {sorted(values)}", f"Q1 = {result[0]}", f"Q2 = {result[1]}", f"Q3 = {result[2]}"]
        return result, steps

    @staticmethod
    def deciles(values):
        result = [Calculator.quantile(values, q) for q in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]]
        steps = [f"Valores ordenados: {sorted(values)}", f"Deciles = {result}"]
        return result, steps

    @staticmethod
    def percentiles(values, p):
        result = Calculator.quantile(values, p / 100)
        steps = [f"Valores ordenados: {sorted(values)}", f"Percentil {p} = {result}"]
        return result, steps

    @staticmethod
    def simple_probability(values):
        favorable = values[0] if len(values) > 0 else 0
        total = values[1] if len(values) > 1 else 0
        result = favorable / total if total else 0
        steps = [f"Eventos favorables: {favorable}", f"Espacio muestral: {total}", f"P(A) = {favorable} / {total} = {result}"]
        return result, steps

    @staticmethod
    def complementary_probability(values):
        probability = values[0] if values else 0
        result = 1 - probability
        steps = [f"P(A^c) = 1 - P(A)", f"P(A^c) = 1 - {probability} = {result}"]
        return result, steps

    @staticmethod
    def addition_rule(values):
        p_a = values[0] if len(values) > 0 else 0
        p_b = values[1] if len(values) > 1 else 0
        p_intersection = values[2] if len(values) > 2 else 0
        result = p_a + p_b - p_intersection
        steps = [f"P(A∪B) = P(A) + P(B) - P(A∩B)", f"P(A∪B) = {p_a} + {p_b} - {p_intersection} = {result}"]
        return result, steps

    @staticmethod
    def conditional_probability(values):
        p_intersection = values[0] if len(values) > 0 else 0
        p_b = values[1] if len(values) > 1 else 0
        result = p_intersection / p_b if p_b else 0
        steps = [f"P(A|B) = P(A∩B) / P(B)", f"P(A|B) = {p_intersection} / {p_b} = {result}"]
        return result, steps

    @staticmethod
    def product_rule(values):
        p_a = values[0] if len(values) > 0 else 0
        p_b_given_a = values[1] if len(values) > 1 else 0
        result = p_a * p_b_given_a
        steps = [f"P(A∩B) = P(A) × P(B|A)", f"P(A∩B) = {p_a} × {p_b_given_a} = {result}"]
        return result, steps

    @staticmethod
    def binomial_probability(n, x, p):
        if not (0 <= p <= 1):
            raise ValueError("La probabilidad debe estar entre 0 y 1")
        if not (0 <= x <= n):
            raise ValueError("x debe estar entre 0 y n")
        if n < 0:
            raise ValueError("n debe ser un valor válido")
        result = comb(n, x) * (p ** x) * ((1 - p) ** (n - x))
        steps = [f"P(X=x) = C({n},{x})·p^{x}·(1-p)^(n-x)", f"P(X={x}) = {result}"]
        return result, steps

    @staticmethod
    def calculate(formula_name, values, parameters=None):
        parameters = parameters or {}
        formula_name = (formula_name or "").lower()

        if "media" in formula_name and "aritm" in formula_name:
            return Calculator.arithmetic_mean(values)
        if "mediana" in formula_name:
            return Calculator.median(values)
        if "moda" in formula_name:
            return Calculator.mode(values)
        if "desviación respecto de la media" in formula_name or "desviacion respecto de la media" in formula_name:
            return Calculator.deviation_from_mean(values)
        if "desviación media" in formula_name or "desviacion media" in formula_name:
            return Calculator.mean_deviation(values)
        if "varianza poblacional" in formula_name:
            return Calculator.population_variance(values)
        if "desviación estándar poblacional" in formula_name or "desviacion estandar poblacional" in formula_name:
            return Calculator.population_std_dev(values)
        if "cuartil" in formula_name:
            return Calculator.quartiles(values)
        if "decil" in formula_name:
            return Calculator.deciles(values)
        if "percentil" in formula_name:
            return Calculator.percentiles(values, parameters.get("percentile", 50))
        if "probabilidad simple" in formula_name:
            return Calculator.simple_probability(values)
        if "complement" in formula_name:
            return Calculator.complementary_probability(values)
        if "regla de la suma" in formula_name:
            return Calculator.addition_rule(values)
        if "condicional" in formula_name:
            return Calculator.conditional_probability(values)
        if "regla del producto" in formula_name:
            return Calculator.product_rule(values)
        if "binomial" in formula_name or "p(x=x)" in formula_name:
            n = values[0] if len(values) > 0 else 0
            x = values[1] if len(values) > 1 else 0
            p = values[2] if len(values) > 2 else 0
            probability, steps = Calculator.binomial_probability(int(n), int(x), p)
            mean = n * p
            variance = n * p * (1 - p)
            std_dev = sqrt(variance)
            steps.extend([f"μ = np = {mean}", f"σ² = np(1-p) = {variance}", f"σ = √(np(1-p)) = {std_dev}"])
            return {
                "probabilidad": probability,
                "media": mean,
                "varianza": variance,
                "desviacion_estandar": std_dev,
            }, steps

        raise ValueError("No hay cálculo implementado para esta fórmula")

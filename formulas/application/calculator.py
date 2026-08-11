from math import comb

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
        if isinstance(values, str):
            return [float(value.strip()) for value in values.split(",") if value.strip()]
        if isinstance(values, list):
            return [float(value) for value in values]
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
    def calculate(formula_id, values):
        if formula_id == 1:
            return Calculator.arithmetic_mean(values)
        if formula_id == 2:
            return Calculator.median(values)
        if formula_id == 3:
            return Calculator.mode(values)
        raise ValueError("No hay cálculo implementado para esta fórmula")

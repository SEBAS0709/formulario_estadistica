import unittest

from formulas.application.calculator import Calculator


class CalculatorTests(unittest.TestCase):
    def test_arithmetic_mean(self):
        result, steps = Calculator.arithmetic_mean([10, 20, 30, 40])
        self.assertEqual(result, 25)
        self.assertTrue(steps)

    def test_population_variance(self):
        result, steps = Calculator.population_variance([2, 4, 6, 8])
        self.assertAlmostEqual(result, 5)
        self.assertTrue(steps)

    def test_binomial_probability(self):
        result, steps = Calculator.binomial_probability(4, 2, 0.5)
        self.assertAlmostEqual(result, 0.375)
        self.assertTrue(steps)


if __name__ == "__main__":
    unittest.main()

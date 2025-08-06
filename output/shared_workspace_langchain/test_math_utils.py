import unittest
from math_utils import MathUtils

class TestMathUtils(unittest.TestCase):

    # Test add method
    def test_add_positive_numbers(self):
        self.assertEqual(MathUtils.add(2, 3), 5)

    def test_add_negative_numbers(self):
        self.assertEqual(MathUtils.add(-2, -3), -5)

    def test_add_mixed_numbers(self):
        self.assertEqual(MathUtils.add(2, -3), -1)

    def test_add_float_numbers(self):
        self.assertAlmostEqual(MathUtils.add(2.5, 3.5), 6.0)

    def test_add_zero(self):
        self.assertEqual(MathUtils.add(5, 0), 5)

    def test_add_type_error(self):
        with self.assertRaises(TypeError) as cm:
            MathUtils.add(1, 'a')
        self.assertEqual(str(cm.exception), "Both inputs must be numbers (int or float).")

    # Test subtract method
    def test_subtract_positive_numbers(self):
        self.assertEqual(MathUtils.subtract(5, 3), 2)

    def test_subtract_negative_numbers(self):
        self.assertEqual(MathUtils.subtract(-5, -3), -2)

    def test_subtract_mixed_numbers(self):
        self.assertEqual(MathUtils.subtract(5, -3), 8)

    def test_subtract_float_numbers(self):
        self.assertAlmostEqual(MathUtils.subtract(5.5, 3.0), 2.5)

    def test_subtract_zero(self):
        self.assertEqual(MathUtils.subtract(5, 0), 5)

    def test_subtract_type_error(self):
        with self.assertRaises(TypeError) as cm:
            MathUtils.subtract('b', 2)
        self.assertEqual(str(cm.exception), "Both inputs must be numbers (int or float).")

    # Test multiply method
    def test_multiply_positive_numbers(self):
        self.assertEqual(MathUtils.multiply(2, 3), 6)

    def test_multiply_negative_numbers(self):
        self.assertEqual(MathUtils.multiply(-2, -3), 6)

    def test_multiply_mixed_numbers(self):
        self.assertEqual(MathUtils.multiply(2, -3), -6)

    def test_multiply_float_numbers(self):
        self.assertAlmostEqual(MathUtils.multiply(2.5, 2.0), 5.0)

    def test_multiply_by_zero(self):
        self.assertEqual(MathUtils.multiply(5, 0), 0)

    def test_multiply_type_error(self):
        with self.assertRaises(TypeError) as cm:
            MathUtils.multiply(2, [3])
        self.assertEqual(str(cm.exception), "Both inputs must be numbers (int or float).")

    # Test divide method
    def test_divide_positive_numbers(self):
        self.assertEqual(MathUtils.divide(6, 3), 2)

    def test_divide_negative_numbers(self):
        self.assertEqual(MathUtils.divide(-6, -3), 2)

    def test_divide_mixed_numbers(self):
        self.assertEqual(MathUtils.divide(6, -3), -2)

    def test_divide_float_numbers(self):
        self.assertAlmostEqual(MathUtils.divide(7.0, 2.0), 3.5)

    def test_divide_by_one(self):
        self.assertEqual(MathUtils.divide(5, 1), 5)

    def test_divide_by_zero_error(self):
        with self.assertRaises(ValueError) as cm:
            MathUtils.divide(5, 0)
        self.assertEqual(str(cm.exception), "Cannot divide by zero.")

    def test_divide_type_error(self):
        with self.assertRaises(TypeError) as cm:
            MathUtils.divide(10, 'x')
        self.assertEqual(str(cm.exception), "Both inputs must be numbers (int or float).")

    # Test power method
    def test_power_positive_exponent(self):
        self.assertEqual(MathUtils.power(2, 3), 8)

    def test_power_negative_exponent(self):
        self.assertAlmostEqual(MathUtils.power(2, -1), 0.5)

    def test_power_zero_exponent(self):
        self.assertEqual(MathUtils.power(5, 0), 1)

    def test_power_float_exponent(self):
        self.assertAlmostEqual(MathUtils.power(4, 0.5), 2.0)

    def test_power_zero_base_positive_exponent(self):
        self.assertEqual(MathUtils.power(0, 5), 0)

    def test_power_zero_base_zero_exponent(self):
        self.assertEqual(MathUtils.power(0, 0), 1) # Python's behavior for 0**0

    def test_power_zero_base_negative_exponent_error(self):
        with self.assertRaises(ValueError) as cm:
            MathUtils.power(0, -2)
        self.assertEqual(str(cm.exception), "Cannot raise zero to a negative power.")

    def test_power_type_error(self):
        with self.assertRaises(TypeError) as cm:
            MathUtils.power(2, 'x')
        self.assertEqual(str(cm.exception), "Both base and exponent must be numbers (int or float).")

if __name__ == '__main__':
    unittest.main()

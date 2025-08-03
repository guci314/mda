
class MathUtils:
    @staticmethod
    def add(a, b):
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Both inputs must be numbers (int or float).")
        return a + b

    @staticmethod
    def subtract(a, b):
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Both inputs must be numbers (int or float).")
        return a - b

    @staticmethod
    def multiply(a, b):
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Both inputs must be numbers (int or float).")
        return a * b

    @staticmethod
    def divide(a, b):
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Both inputs must be numbers (int or float).")
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b

    @staticmethod
    def power(base, exponent):
        if not isinstance(base, (int, float)) or not isinstance(exponent, (int, float)):
            raise TypeError("Both base and exponent must be numbers (int or float).")
        if base == 0 and exponent < 0:
            raise ValueError("Cannot raise 0 to a negative power.")
        return base ** exponent

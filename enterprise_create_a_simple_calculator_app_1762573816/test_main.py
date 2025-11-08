import unittest
from calculator import add, subtract, multiply, divide
from typing import Union

class TestCalculator(unittest.TestCase):
    """
    Test suite for the calculator functions (add, subtract, multiply, divide).
    """

    def test_add_positive_numbers(self) -> None:
        """
        Test addition of two positive numbers.
        """
        self.assertEqual(add(2, 3), 5, "Addition of positive numbers failed.")

    def test_add_negative_numbers(self) -> None:
        """
        Test addition of two negative numbers.
        """
        self.assertEqual(add(-2, -3), -5, "Addition of negative numbers failed.")

    def test_add_positive_and_negative_numbers(self) -> None:
        """
        Test addition of a positive and a negative number.
        """
        self.assertEqual(add(5, -2), 3, "Addition of positive and negative numbers failed.")

    def test_add_zero(self) -> None:
        """
        Test addition with zero.
        """
        self.assertEqual(add(5, 0), 5, "Addition with zero failed.")

    def test_subtract_positive_numbers(self) -> None:
        """
        Test subtraction of two positive numbers.
        """
        self.assertEqual(subtract(5, 2), 3, "Subtraction of positive numbers failed.")

    def test_subtract_negative_numbers(self) -> None:
        """
        Test subtraction of two negative numbers.
        """
        self.assertEqual(subtract(-2, -3), 1, "Subtraction of negative numbers failed.")

    def test_subtract_positive_and_negative_numbers(self) -> None:
        """
        Test subtraction of a positive and a negative number.
        """
        self.assertEqual(subtract(5, -2), 7, "Subtraction of positive and negative numbers failed.")

    def test_subtract_zero(self) -> None:
        """
        Test subtraction with zero.
        """
        self.assertEqual(subtract(5, 0), 5, "Subtraction with zero failed.")

    def test_multiply_positive_numbers(self) -> None:
        """
        Test multiplication of two positive numbers.
        """
        self.assertEqual(multiply(2, 3), 6, "Multiplication of positive numbers failed.")

    def test_multiply_negative_numbers(self) -> None:
        """
        Test multiplication of two negative numbers.
        """
        self.assertEqual(multiply(-2, -3), 6, "Multiplication of negative numbers failed.")

    def test_multiply_positive_and_negative_numbers(self) -> None:
        """
        Test multiplication of a positive and a negative number.
        """
        self.assertEqual(multiply(5, -2), -10, "Multiplication of positive and negative numbers failed.")

    def test_multiply_zero(self) -> None:
        """
        Test multiplication with zero.
        """
        self.assertEqual(multiply(5, 0), 0, "Multiplication with zero failed.")

    def test_divide_positive_numbers(self) -> None:
        """
        Test division of two positive numbers.
        """
        self.assertEqual(divide(6, 2), 3, "Division of positive numbers failed.")

    def test_divide_negative_numbers(self) -> None:
        """
        Test division of two negative numbers.
        """
        self.assertEqual(divide(-6, -2), 3, "Division of negative numbers failed.")

    def test_divide_positive_and_negative_numbers(self) -> None:
        """
        Test division of a positive and a negative number.
        """
        self.assertEqual(divide(6, -2), -3, "Division of positive and negative numbers failed.")

    def test_divide_by_zero(self) -> None:
        """
        Test division by zero.  Ensures ZeroDivisionError is raised.
        """
        with self.assertRaises(ZeroDivisionError, msg="Division by zero should raise an error."):
            divide(5, 0)

    def test_divide_zero_by_number(self) -> None:
        """
        Test division of zero by a number.
        """
        self.assertEqual(divide(0, 5), 0, "Division of zero by a number failed.")

if __name__ == '__main__':
    unittest.main()
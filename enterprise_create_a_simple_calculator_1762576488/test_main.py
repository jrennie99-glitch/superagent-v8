import unittest
from typing import Union
from unittest.mock import patch
import io
import sys
import os

# Import the calculator functions from the main script
try:
    from main import add, subtract, multiply, divide  # type: ignore[import]
except ImportError:
    print("Error: Unable to import calculator functions from 'main.py'. "
          "Ensure 'main.py' exists and contains the required functions.")
    sys.exit(1)


class TestCalculator(unittest.TestCase):
    """
    Unit tests for the calculator functions.
    """

    def test_add_positive_numbers(self) -> None:
        """
        Test adding two positive numbers.
        """
        self.assertEqual(add(2, 3), 5, "Addition of positive numbers failed.")

    def test_add_negative_numbers(self) -> None:
        """
        Test adding two negative numbers.
        """
        self.assertEqual(add(-2, -3), -5, "Addition of negative numbers failed.")

    def test_add_positive_and_negative_numbers(self) -> None:
        """
        Test adding a positive and a negative number.
        """
        self.assertEqual(add(5, -2), 3, "Addition of positive and negative numbers failed.")

    def test_add_zero(self) -> None:
        """
        Test adding zero to a number.
        """
        self.assertEqual(add(7, 0), 7, "Addition with zero failed.")

    def test_subtract_positive_numbers(self) -> None:
        """
        Test subtracting two positive numbers.
        """
        self.assertEqual(subtract(5, 2), 3, "Subtraction of positive numbers failed.")

    def test_subtract_negative_numbers(self) -> None:
        """
        Test subtracting two negative numbers.
        """
        self.assertEqual(subtract(-2, -3), 1, "Subtraction of negative numbers failed.")

    def test_subtract_positive_and_negative_numbers(self) -> None:
        """
        Test subtracting a positive and a negative number.
        """
        self.assertEqual(subtract(5, -2), 7, "Subtraction of positive and negative numbers failed.")

    def test_subtract_zero(self) -> None:
        """
        Test subtracting zero from a number.
        """
        self.assertEqual(subtract(7, 0), 7, "Subtraction with zero failed.")

    def test_multiply_positive_numbers(self) -> None:
        """
        Test multiplying two positive numbers.
        """
        self.assertEqual(multiply(2, 3), 6, "Multiplication of positive numbers failed.")

    def test_multiply_negative_numbers(self) -> None:
        """
        Test multiplying two negative numbers.
        """
        self.assertEqual(multiply(-2, -3), 6, "Multiplication of negative numbers failed.")

    def test_multiply_positive_and_negative_numbers(self) -> None:
        """
        Test multiplying a positive and a negative number.
        """
        self.assertEqual(multiply(5, -2), -10, "Multiplication of positive and negative numbers failed.")

    def test_multiply_zero(self) -> None:
        """
        Test multiplying a number by zero.
        """
        self.assertEqual(multiply(7, 0), 0, "Multiplication with zero failed.")

    def test_divide_positive_numbers(self) -> None:
        """
        Test dividing two positive numbers.
        """
        self.assertEqual(divide(6, 2), 3, "Division of positive numbers failed.")

    def test_divide_negative_numbers(self) -> None:
        """
        Test dividing two negative numbers.
        """
        self.assertEqual(divide(-6, -2), 3, "Division of negative numbers failed.")

    def test_divide_positive_and_negative_numbers(self) -> None:
        """
        Test dividing a positive and a negative number.
        """
        self.assertEqual(divide(6, -2), -3, "Division of positive and negative numbers failed.")

    def test_divide_by_zero(self) -> None:
        """
        Test dividing by zero.  Ensures a ValueError is raised.
        """
        with self.assertRaises(ValueError):
            divide(7, 0)  # Division by zero should raise an error

    def test_divide_zero_by_number(self) -> None:
        """
        Test dividing zero by a number.
        """
        self.assertEqual(divide(0, 7), 0, "Division of zero by a number failed.")

    def test_add_invalid_input(self) -> None:
        """
        Test addition with invalid input (string).
        """
        with self.assertRaises(TypeError):
            add("a", 5)  # type: ignore[arg-type] # Intentionally passing incorrect type

    def test_subtract_invalid_input(self) -> None:
        """
        Test subtraction with invalid input (string).
        """
        with self.assertRaises(TypeError):
            subtract(5, "a")  # type: ignore[arg-type] # Intentionally passing incorrect type

    def test_multiply_invalid_input(self) -> None:
        """
        Test multiplication with invalid input (string).
        """
        with self.assertRaises(TypeError):
            multiply("a", 5) # type: ignore[arg-type] # Intentionally passing incorrect type

    def test_divide_invalid_input(self) -> None:
        """
        Test division with invalid input (string).
        """
        with self.assertRaises(TypeError):
            divide(5, "a") # type: ignore[arg-type] # Intentionally passing incorrect type

if __name__ == '__main__':
    unittest.main()
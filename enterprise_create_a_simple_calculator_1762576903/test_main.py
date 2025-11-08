import unittest
from typing import Union

# Assuming the calculator logic is in a file named 'main.py'
from main import add, subtract, multiply, divide, CalculatorError


class TestCalculator(unittest.TestCase):
    """
    Test suite for the calculator functions.
    Covers addition, subtraction, multiplication, and division operations.
    Includes tests for valid inputs, edge cases, and error handling.
    """

    def test_add_positive_numbers(self) -> None:
        """Test adding two positive numbers."""
        self.assertEqual(add(2, 3), 5)

    def test_add_negative_numbers(self) -> None:
        """Test adding two negative numbers."""
        self.assertEqual(add(-2, -3), -5)

    def test_add_positive_and_negative(self) -> None:
        """Test adding a positive and a negative number."""
        self.assertEqual(add(2, -3), -1)

    def test_add_zero(self) -> None:
        """Test adding zero to a number."""
        self.assertEqual(add(5, 0), 5)

    def test_subtract_positive_numbers(self) -> None:
        """Test subtracting two positive numbers."""
        self.assertEqual(subtract(5, 2), 3)

    def test_subtract_negative_numbers(self) -> None:
        """Test subtracting two negative numbers."""
        self.assertEqual(subtract(-5, -2), -3)

    def test_subtract_positive_and_negative(self) -> None:
        """Test subtracting a positive and a negative number."""
        self.assertEqual(subtract(5, -2), 7)

    def test_subtract_zero(self) -> None:
        """Test subtracting zero from a number."""
        self.assertEqual(subtract(5, 0), 5)

    def test_multiply_positive_numbers(self) -> None:
        """Test multiplying two positive numbers."""
        self.assertEqual(multiply(2, 3), 6)

    def test_multiply_negative_numbers(self) -> None:
        """Test multiplying two negative numbers."""
        self.assertEqual(multiply(-2, -3), 6)

    def test_multiply_positive_and_negative(self) -> None:
        """Test multiplying a positive and a negative number."""
        self.assertEqual(multiply(2, -3), -6)

    def test_multiply_zero(self) -> None:
        """Test multiplying by zero."""
        self.assertEqual(multiply(5, 0), 0)

    def test_divide_positive_numbers(self) -> None:
        """Test dividing two positive numbers."""
        self.assertEqual(divide(6, 2), 3)

    def test_divide_negative_numbers(self) -> None:
        """Test dividing two negative numbers."""
        self.assertEqual(divide(-6, -2), 3)

    def test_divide_positive_and_negative(self) -> None:
        """Test dividing a positive and a negative number."""
        self.assertEqual(divide(6, -2), -3)

    def test_divide_by_one(self) -> None:
        """Test dividing by one."""
        self.assertEqual(divide(5, 1), 5)

    def test_divide_by_zero(self) -> None:
        """Test dividing by zero raises a CalculatorError."""
        with self.assertRaises(CalculatorError) as context:
            divide(5, 0)
        self.assertEqual(str(context.exception), "Cannot divide by zero.")

    def test_add_large_numbers(self) -> None:
        """Test adding large numbers to check for overflow issues (if applicable based on the implementation)."""
        large_number: int = 2**63 - 1
        self.assertEqual(add(large_number, 1), large_number + 1)

    def test_subtract_large_numbers(self) -> None:
        """Test subtracting large numbers to check for underflow issues (if applicable based on the implementation)."""
        large_number: int = 2**63 - 1
        self.assertEqual(subtract(1, large_number), 1 - large_number)

    def test_multiply_large_numbers(self) -> None:
        """Test multiplying large numbers, handling potential overflow."""
        num1: int = 2**31 - 1
        num2: int = 2
        self.assertEqual(multiply(num1, num2), num1 * num2)  # Assuming implementation handles overflows appropriately

    def test_divide_large_numbers(self) -> None:
        """Test dividing large numbers and handle potential errors."""
        num1: int = 2**63 - 1
        num2: int = 2
        self.assertEqual(divide(num1, num2), num1 / num2)

    def test_input_validation(self) -> None:
        """
        Tests the function with invalid inputs. We are only testing float values as valid number inputs in this case.
        """
        with self.assertRaises(TypeError):
            add("a", 1)  # type: ignore
        with self.assertRaises(TypeError):
            subtract(1, "b")  # type: ignore
        with self.assertRaises(TypeError):
            multiply(1, [1,2]) # type: ignore
        with self.assertRaises(TypeError):
            divide({"a": 1}, 1) # type: ignore

if __name__ == '__main__':
    unittest.main()
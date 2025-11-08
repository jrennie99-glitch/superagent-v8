"""
Main entry point for the simple calculator application.
Handles user input, performs calculations, and displays results.
"""

import logging
import os
import operator
from typing import Dict, Callable, Union, Optional

# Configure logging
logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Define supported operations and their corresponding functions
OPERATIONS: Dict[str, Callable[[float, float], float]] = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,  # Changed div to truediv for float division
    "^": operator.pow,
}


def calculate(num1: float, num2: float, operation: str) -> Optional[float]:
    """
    Performs a calculation based on the provided numbers and operation.

    Args:
        num1: The first number (float).
        num2: The second number (float).
        operation: The operation to perform (+, -, *, /, ^).

    Returns:
        The result of the calculation (float), or None if an error occurs.
    """
    if operation not in OPERATIONS:
        logging.error(f"Invalid operation: {operation}")
        return None

    try:
        result = OPERATIONS[operation](num1, num2)
        return result
    except ZeroDivisionError:
        logging.error("Division by zero error.")
        print("Error: Cannot divide by zero.")  # Inform user as well
        return None
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")
        print("An unexpected error occurred. Please check the logs.") # inform user
        return None


def get_user_input(prompt: str) -> str:
    """
    Gets user input with a given prompt.

    Args:
        prompt: The message to display to the user.

    Returns:
        The user's input as a string.
    """
    return input(prompt)


def parse_number(input_str: str) -> Optional[float]:
    """
    Safely parses a string into a float.  Handles potential ValueError.

    Args:
        input_str: The string to parse.

    Returns:
        The float representation of the string, or None if parsing fails.
    """
    try:
        return float(input_str)
    except ValueError:
        logging.error(f"Invalid number format: {input_str}")
        print("Error: Invalid number format. Please enter a valid number.")  # Inform user
        return None


def main() -> None:
    """
    The main function of the calculator application.
    Handles user interaction and performs calculations.
    """
    while True:
        try:
            num1_str = get_user_input("Enter the first number: ")
            num1 = parse_number(num1_str)
            if num1 is None:
                continue  # Restart loop if parsing failed

            num2_str = get_user_input("Enter the second number: ")
            num2 = parse_number(num2_str)
            if num2 is None:
                continue  # Restart loop if parsing failed

            operation = get_user_input("Enter the operation (+, -, *, /, ^): ")

            result = calculate(num1, num2, operation)

            if result is not None:
                print(f"Result: {result}")

        except KeyboardInterrupt:
            print("\nCalculator terminated by user.")
            break
        except Exception as e:
            logging.exception(f"An unexpected error occurred in main loop: {e}")
            print("An unexpected error occurred. Please check the logs.")  # Inform User
        finally:
            continue_calculation = get_user_input("Do you want to perform another calculation? (yes/no): ")
            if continue_calculation.lower() != "yes":
                print("Calculator shutting down.")
                break


if __name__ == "__main__":
    main()
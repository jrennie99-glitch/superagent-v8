import logging

# Configure logging for the application
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def safe_float_input(prompt: str) -> float:
    """
    Prompts the user for a floating-point number and validates the input.

    Args:
        prompt: The message to display to the user.

    Returns:
        The validated floating-point number.

    Raises:
        ValueError: If the input is not a valid number.
    """
    while True:
        try:
            user_input = input(prompt)
            number = float(user_input)
            return number
        except ValueError:
            logging.error(f"Invalid input: '{user_input}'. Please enter a valid number.")
            print("Invalid input. Please enter a valid number.")
        except Exception as e:
            logging.exception(f"An unexpected error occurred during number input: {e}")
            print("An unexpected error occurred. Please try again.")


def safe_operator_input() -> str:
    """
    Prompts the user for an operator (+, -, *, /) and validates the input.

    Returns:
        The validated operator.

    Raises:
        ValueError: If the input is not a valid operator.
    """
    valid_operators = ["+", "-", "*", "/"]
    while True:
        operator = input("Enter an operator (+, -, *, /): ")
        if operator in valid_operators:
            return operator
        else:
            logging.error(f"Invalid operator: '{operator}'. Please enter +, -, *, or /.")
            print("Invalid operator. Please enter +, -, *, or /.")


def calculate(num1: float, num2: float, operator: str) -> float:
    """
    Performs a calculation based on the given numbers and operator.

    Args:
        num1: The first number.
        num2: The second number.
        operator: The operator to use.

    Returns:
        The result of the calculation.

    Raises:
        ValueError: If the operator is invalid.
        ZeroDivisionError: If attempting to divide by zero.
    """
    try:
        if operator == "+":
            return num1 + num2
        elif operator == "-":
            return num1 - num2
        elif operator == "*":
            return num1 * num2
        elif operator == "/":
            if num2 == 0:
                logging.error("Division by zero is not allowed.")
                raise ZeroDivisionError("Division by zero is not allowed.")
            return num1 / num2
        else:
            logging.error(f"Invalid operator: {operator}")
            raise ValueError(f"Invalid operator: {operator}")
    except ZeroDivisionError as zde:
        print(f"Error: {zde}")
        return float('inf')  # Return infinity to indicate the error in a numerical way.
    except ValueError as ve:
        print(f"Error: {ve}")
        raise  # Re-raise the exception to be handled by the caller.
    except Exception as e:
        logging.exception(f"An unexpected error occurred during calculation: {e}")
        print("An unexpected error occurred. Please try again.")
        raise


def main() -> None:
    """
    The main function of the calculator application.
    """
    try:
        logging.info("Starting the calculator application.")
        num1 = safe_float_input("Enter the first number: ")
        operator = safe_operator_input()
        num2 = safe_float_input("Enter the second number: ")

        result = calculate(num1, num2, operator)
        print(f"Result: {result}")

        logging.info("Calculator application completed successfully.")

    except Exception as e:
        logging.critical(f"An unhandled exception occurred: {e}")
        print("A critical error occurred. Please check the logs for details.")


if __name__ == "__main__":
    main()
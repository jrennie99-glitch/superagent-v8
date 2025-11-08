#!/usr/bin/env python3

"""
Entry point for a simple calculator app backend.
This module sets up a basic Flask server to handle calculator operations.
"""

import os
import logging
from typing import Dict, Tuple, Union

from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest, InternalServerError, HTTPException

# Initialize Flask app
app = Flask(__name__)

# Configure logging (for production use)
logging.basicConfig(
    level=logging.INFO,  # Set desired logging level
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],  # Log to console
)


def safe_divide(numerator: Union[int, float], denominator: Union[int, float]) -> Union[int, float]:
    """
    Safely divides two numbers, handling the case of division by zero.

    Args:
        numerator: The number to be divided.
        denominator: The number to divide by.

    Returns:
        The result of the division.

    Raises:
        ValueError: If the denominator is zero.
    """
    if denominator == 0:
        raise ValueError("Cannot divide by zero")
    return numerator / denominator


@app.route('/calculate', methods=['POST'])
def calculate() -> Tuple[jsonify, int]:
    """
    Endpoint for performing calculations.

    Handles POST requests with JSON data containing 'operation' and 'numbers'.
    Valid operations are 'add', 'subtract', 'multiply', and 'divide'.
    'numbers' should be a list of two numerical values.

    Returns:
        A JSON response containing the result of the calculation.

    Raises:
        BadRequest: If the request data is invalid or missing.
        InternalServerError: If an unexpected error occurs during calculation.
    """
    try:
        data: Dict = request.get_json()
        logging.info(f"Received calculation request: {data}")  # Log request data

        if not data or 'operation' not in data or 'numbers' not in data:
            raise BadRequest("Invalid request data.  'operation' and 'numbers' are required.")

        operation: str = data['operation']
        numbers: list = data['numbers']  # Assuming numbers is a list

        if not isinstance(numbers, list) or len(numbers) != 2:
            raise BadRequest("Invalid 'numbers' format.  Must be a list of two numerical values.")

        try:
            num1: float = float(numbers[0])
            num2: float = float(numbers[1])
        except (ValueError, TypeError):
            raise BadRequest("Invalid 'numbers' values.  Must be numerical.")

        result: Union[int, float]

        if operation == 'add':
            result = num1 + num2
        elif operation == 'subtract':
            result = num1 - num2
        elif operation == 'multiply':
            result = num1 * num2
        elif operation == 'divide':
            result = safe_divide(num1, num2)
        else:
            raise BadRequest("Invalid operation.  Supported operations are 'add', 'subtract', 'multiply', 'divide'.")

        response_data: Dict[str, Union[str, float, int]] = {'result': result}
        logging.info(f"Calculation successful.  Result: {result}")  # Log the result

        return jsonify(response_data), 200  # Return 200 OK

    except BadRequest as e:
        logging.warning(f"Bad Request: {str(e)}")  # Log the error
        return jsonify({'error': str(e)}), 400  # Return 400 Bad Request
    except ValueError as e:  # Specifically catch ValueError, e.g., division by zero.
        logging.warning(f"Value Error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.exception("An unexpected error occurred during calculation.")  # Log the full exception
        return jsonify({'error': 'Internal Server Error'}), 500  # Return 500 Internal Server Error


@app.errorhandler(HTTPException)
def handle_exception(e: HTTPException) -> Tuple[jsonify, int]:
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = jsonify({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    }).get_data(mimetype="application/json")
    response.content_type = "application/json"
    return response, e.code


if __name__ == '__main__':
    # Get the port from the environment, default to 5000
    port: int = int(os.environ.get('PORT', 5000))
    # Run the app in production mode (set debug=False for production)
    app.run(debug=False, host='0.0.0.0', port=port)
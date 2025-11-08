from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from typing import List, Dict, Any
from werkzeug.exceptions import HTTPException
import os
import logging

# Initialize Flask application
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database Configuration
# Use an environment variable for the database URI for flexibility and security
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///./todos.db')  # Default to SQLite for local development
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking for performance

# Initialize SQLAlchemy
db = SQLAlchemy(app)


# Define Todo Model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self) -> str:
        return f'<Todo {self.id}: {self.task}>'


# Create database tables if they don't exist upon app startup
with app.app_context():
    db.create_all()


# Error Handling
@app.errorhandler(HTTPException)
def handle_exception(e: HTTPException) -> tuple[jsonify, int]:
    """Handles HTTP exceptions and returns a JSON response."""
    response = {
        "code": e.code,
        "name": e.name,
        "description": e.description,
    }
    logging.error(f"HTTP Exception: {e.code} - {e.name} - {e.description}")  # Log the error
    return jsonify(response), e.code


@app.errorhandler(Exception)
def handle_generic_exception(e: Exception) -> tuple[jsonify, int]:
    """Handles generic exceptions and returns a JSON response."""
    logging.exception("An unexpected error occurred:")  # Log the full exception including traceback
    response = {
        "code": 500,
        "name": "Internal Server Error",
        "description": "An unexpected error occurred. Please try again later.",
    }
    return jsonify(response), 500


# API Endpoints
@app.route('/todos', methods=['GET'])
def get_todos() -> jsonify:
    """
    Retrieves all todos from the database.
    Returns:
        jsonify: A JSON response containing a list of all todos.
    """
    try:
        todos: List[Todo] = Todo.query.all()
        todo_list: List[Dict[str, Any]] = [{'id': todo.id, 'task': todo.task, 'completed': todo.completed} for todo in todos]
        logging.info("Successfully retrieved all todos.")
        return jsonify(todos=todo_list), 200
    except Exception as e:
        logging.error(f"Error retrieving todos: {e}")
        raise


@app.route('/todos', methods=['POST'])
def create_todo() -> jsonify:
    """
    Creates a new todo in the database.
    Receives the task description from the request body.
    Returns:
        jsonify: A JSON response containing the newly created todo.
    """
    try:
        data: Dict[str, str] = request.get_json()
        if not data or 'task' not in data:
            logging.warning("Invalid request: 'task' is missing in the request body.")
            return jsonify({'message': 'Task description is required.'}), 400

        new_todo: Todo = Todo(task=data['task'])
        db.session.add(new_todo)
        db.session.commit()
        logging.info(f"Successfully created todo with id: {new_todo.id}")
        return jsonify({'id': new_todo.id, 'task': new_todo.task, 'completed': new_todo.completed}), 201
    except Exception as e:
        logging.error(f"Error creating todo: {e}")
        db.session.rollback()  # Rollback in case of error during database operation
        raise


@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id: int) -> jsonify:
    """
    Retrieves a specific todo from the database.
    Args:
        todo_id (int): The ID of the todo to retrieve.
    Returns:
        jsonify: A JSON response containing the requested todo, or an error if not found.
    """
    try:
        todo: Todo = Todo.query.get_or_404(todo_id)  # Returns 404 if not found
        logging.info(f"Successfully retrieved todo with id: {todo_id}")
        return jsonify({'id': todo.id, 'task': todo.task, 'completed': todo.completed}), 200
    except Exception as e:
        logging.error(f"Error retrieving todo with id {todo_id}: {e}")
        raise


@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id: int) -> jsonify:
    """
    Updates a specific todo in the database.
    Receives the updated task description and completion status from the request body.
    Args:
        todo_id (int): The ID of the todo to update.
    Returns:
        jsonify: A JSON response containing the updated todo, or an error if not found.
    """
    try:
        todo: Todo = Todo.query.get_or_404(todo_id)
        data: Dict[str, Any] = request.get_json()

        if not data:
            logging.warning("Invalid request: Request body is empty.")
            return jsonify({'message': 'Request body cannot be empty.'}), 400

        if 'task' in data:
            todo.task = data['task']
        if 'completed' in data:
            todo.completed = data['completed']

        db.session.commit()
        logging.info(f"Successfully updated todo with id: {todo_id}")
        return jsonify({'id': todo.id, 'task': todo.task, 'completed': todo.completed}), 200
    except Exception as e:
        logging.error(f"Error updating todo with id {todo_id}: {e}")
        db.session.rollback()
        raise


@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id: int) -> jsonify:
    """
    Deletes a specific todo from the database.
    Args:
        todo_id (int): The ID of the todo to delete.
    Returns:
        jsonify: A success message if the todo was deleted, or an error if not found.
    """
    try:
        todo: Todo = Todo.query.get_or_404(todo_id)
        db.session.delete(todo)
        db.session.commit()
        logging.info(f"Successfully deleted todo with id: {todo_id}")
        return jsonify({'message': 'Todo deleted successfully.'}), 200
    except Exception as e:
        logging.error(f"Error deleting todo with id {todo_id}: {e}")
        db.session.rollback()
        raise


if __name__ == '__main__':
    # Run the Flask application
    # Use environment variables for host and port, defaulting to localhost:5000
    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    app.run(host=host, port=port, debug=False)  #  Disable debug mode in production
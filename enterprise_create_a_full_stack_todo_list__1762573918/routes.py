from typing import List, Dict, Any
from flask import Blueprint, request, jsonify
from flask import current_app
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
from .models import Task  # Assuming models.py is in the same directory
from . import db  # Assuming db (db = SQLAlchemy()) is initialized in __init__.py
import logging

# Configure logging
logger = logging.getLogger(__name__)


api = Blueprint('api', __name__, url_prefix='/api/tasks')


@api.route('', methods=['GET'])
def list_tasks() -> List[Dict[str, Any]]:
    """
    Retrieves a list of all tasks.

    Returns:
        A list of task dictionaries.  Each dictionary represents a task.
        Returns an empty list if no tasks are found.

    Raises:
        InternalServerError:  If there's an unexpected error during database interaction.
    """
    try:
        tasks = Task.query.all()
        task_list = [{"id": task.id, "title": task.title, "completed": task.completed} for task in tasks]
        return jsonify(task_list)
    except Exception as e:
        logger.exception("Error retrieving tasks: %s", e)
        raise InternalServerError("Failed to retrieve tasks.")


@api.route('', methods=['POST'])
def create_task() -> Dict[str, Any]:
    """
    Creates a new task.

    Expects a JSON payload with a 'title' field.

    Returns:
        A dictionary representing the newly created task.

    Raises:
        BadRequest: If the request body is missing the 'title' field or if the title is invalid.
        InternalServerError: If there's an unexpected error during database interaction.
    """
    try:
        data = request.get_json()
        if not data or 'title' not in data:
            raise BadRequest("Missing 'title' in request body.")

        title = data['title']
        if not isinstance(title, str) or not title.strip():
            raise BadRequest("Invalid 'title' format.  Must be a non-empty string.")

        new_task = Task(title=title)
        db.session.add(new_task)
        db.session.commit()

        return jsonify({"id": new_task.id, "title": new_task.title, "completed": new_task.completed}), 201  # 201 Created
    except BadRequest as e:
        raise e # Re-raise the exception to be caught by the error handler
    except Exception as e:
        db.session.rollback()  # Rollback in case of errors during database interaction
        logger.exception("Error creating task: %s", e)
        raise InternalServerError("Failed to create task.")


@api.route('/<int:task_id>', methods=['GET'])
def get_task(task_id: int) -> Dict[str, Any]:
    """
    Retrieves a specific task by its ID.

    Args:
        task_id: The ID of the task to retrieve.

    Returns:
        A dictionary representing the task.

    Raises:
        NotFound: If the task with the given ID does not exist.
        InternalServerError: If there's an unexpected error during database interaction.
    """
    try:
        task = Task.query.get(task_id)
        if not task:
            raise NotFound(f"Task with ID {task_id} not found.")
        return jsonify({"id": task.id, "title": task.title, "completed": task.completed})
    except NotFound as e:
        raise e  # Re-raise NotFound to be handled by errorhandler.
    except Exception as e:
        logger.exception("Error retrieving task %d: %s", task_id, e)
        raise InternalServerError("Failed to retrieve task.")


@api.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id: int) -> Dict[str, Any]:
    """
    Updates a specific task by its ID.

    Expects a JSON payload with 'title' and/or 'completed' fields.

    Args:
        task_id: The ID of the task to update.

    Returns:
        A dictionary representing the updated task.

    Raises:
        BadRequest: If the request body is missing the required fields or if the data is invalid.
        NotFound: If the task with the given ID does not exist.
        InternalServerError: If there's an unexpected error during database interaction.
    """
    try:
        task = Task.query.get(task_id)
        if not task:
            raise NotFound(f"Task with ID {task_id} not found.")

        data = request.get_json()
        if not data:
            raise BadRequest("Request body cannot be empty.")

        if 'title' in data:
            title = data['title']
            if not isinstance(title, str) or not title.strip():
                raise BadRequest("Invalid 'title' format.  Must be a non-empty string.")
            task.title = title

        if 'completed' in data:
            completed = data['completed']
            if not isinstance(completed, bool):
                raise BadRequest("Invalid 'completed' format. Must be a boolean.")
            task.completed = completed

        db.session.commit()
        return jsonify({"id": task.id, "title": task.title, "completed": task.completed})
    except BadRequest as e:
        raise e # Re-raise the exception
    except NotFound as e:
        raise e # Re-raise the exception
    except Exception as e:
        db.session.rollback()
        logger.exception("Error updating task %d: %s", task_id, e)
        raise InternalServerError("Failed to update task.")


@api.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id: int) -> str:
    """
    Deletes a specific task by its ID.

    Args:
        task_id: The ID of the task to delete.

    Returns:
        A success message.

    Raises:
        NotFound: If the task with the given ID does not exist.
        InternalServerError: If there's an unexpected error during database interaction.
    """
    try:
        task = Task.query.get(task_id)
        if not task:
            raise NotFound(f"Task with ID {task_id} not found.")

        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": f"Task {task_id} deleted successfully."}), 200
    except NotFound as e:
        raise e
    except Exception as e:
        db.session.rollback()
        logger.exception("Error deleting task %d: %s", task_id, e)
        raise InternalServerError("Failed to delete task.")


@api.errorhandler(BadRequest)
def handle_bad_request(error: BadRequest) -> tuple[Dict[str, str], int]:
    """Handles BadRequest exceptions (status code 400)."""
    logger.warning("Bad Request: %s", error.description)
    return jsonify({'error': 'Bad Request', 'message': error.description}), 400


@api.errorhandler(NotFound)
def handle_not_found(error: NotFound) -> tuple[Dict[str, str], int]:
    """Handles NotFound exceptions (status code 404)."""
    logger.warning("Not Found: %s", error.description)
    return jsonify({'error': 'Not Found', 'message': error.description}), 404


@api.errorhandler(InternalServerError)
def handle_internal_server_error(error: InternalServerError) -> tuple[Dict[str, str], int]:
    """Handles InternalServerError exceptions (status code 500)."""
    logger.error("Internal Server Error: %s", error)
    return jsonify({'error': 'Internal Server Error', 'message': 'An unexpected error occurred.'}), 500


@api.errorhandler(Exception)
def handle_generic_error(error) -> tuple[Dict[str, str], int]:
    """Handles any unhandled exception (status code 500).
       This is a safety net to catch unexpected errors.
    """
    logger.exception("Unhandled exception: %s", error)
    return jsonify({'error': 'Internal Server Error', 'message': 'An unexpected error occurred.'}), 500
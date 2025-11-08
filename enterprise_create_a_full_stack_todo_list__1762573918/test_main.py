import os
import tempfile
import pytest
from typing import Generator
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from main import app, db, Todo  # Assuming your main app file is named 'main.py'


@pytest.fixture(scope="session")
def test_app() -> Generator[Flask, None, None]:
    """
    Fixture to create a test Flask application with an in-memory SQLite database.
    """
    # Create a temporary file for the SQLite database
    db_fd, db_path = tempfile.mkstemp()

    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'  # In-memory SQLite for testing
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable tracking modifications for efficiency

    with app.app_context():
        db.create_all()

    yield app

    # Clean up after testing
    os.close(db_fd)
    os.unlink(db_path)  # Delete the temporary database file


@pytest.fixture(scope="session")
def test_client(test_app: Flask) -> FlaskClient:
    """
    Fixture to create a test client for the Flask application.
    """
    return test_app.test_client()


@pytest.fixture(scope="session")
def test_db(test_app: Flask) -> Generator[Session, None, None]:
    """
    Fixture to provide a database session for testing.
    """
    engine = create_engine(test_app.config['SQLALCHEMY_DATABASE_URI'])
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db_session = TestingSessionLocal()

    yield db_session

    db_session.close()


@pytest.fixture(scope="function", autouse=True)
def setup_database(test_db: Session) -> Generator[None, None, None]:
    """
    Fixture to set up and tear down the database for each test function.
    Ensures a clean state before and after each test.
    """
    # Start a new transaction before each test
    test_db.begin()
    yield  # Run the test
    # Rollback the transaction after each test to clear any changes made by the test
    test_db.rollback()


def test_add_todo(test_client: FlaskClient, test_db: Session) -> None:
    """
    Test case to verify adding a new todo item.
    """
    response = test_client.post('/todos', json={'task': 'Buy groceries'})
    assert response.status_code == 201  # Created
    data = response.get_json()
    assert data['task'] == 'Buy groceries'
    assert data['completed'] is False
    assert 'id' in data

    # Verify the todo was added to the database
    todo = test_db.query(Todo).filter_by(id=data['id']).first()
    assert todo is not None
    assert todo.task == 'Buy groceries'


def test_get_todos(test_client: FlaskClient, test_db: Session) -> None:
    """
    Test case to verify retrieving all todo items.
    """
    # Add some todos to the database for testing
    todo1 = Todo(task='Walk the dog')
    todo2 = Todo(task='Do laundry')
    test_db.add_all([todo1, todo2])
    test_db.commit()

    response = test_client.get('/todos')
    assert response.status_code == 200  # OK
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]['task'] == 'Walk the dog'
    assert data[1]['task'] == 'Do laundry'


def test_get_todo(test_client: FlaskClient, test_db: Session) -> None:
    """
    Test case to verify retrieving a single todo item by ID.
    """
    # Add a todo to the database for testing
    todo = Todo(task='Pay bills')
    test_db.add(todo)
    test_db.commit()

    response = test_client.get(f'/todos/{todo.id}')
    assert response.status_code == 200  # OK
    data = response.get_json()
    assert data['task'] == 'Pay bills'


def test_get_todo_not_found(test_client: FlaskClient) -> None:
    """
    Test case to verify retrieving a non-existent todo item.
    """
    response = test_client.get('/todos/999')  # Assuming ID 999 doesn't exist
    assert response.status_code == 404  # Not Found
    data = response.get_json()
    assert data['message'] == 'Todo not found'


def test_update_todo(test_client: FlaskClient, test_db: Session) -> None:
    """
    Test case to verify updating a todo item.
    """
    # Add a todo to the database for testing
    todo = Todo(task='Read a book', completed=False)
    test_db.add(todo)
    test_db.commit()

    response = test_client.put(f'/todos/{todo.id}', json={'task': 'Read more', 'completed': True})
    assert response.status_code == 200  # OK
    data = response.get_json()
    assert data['task'] == 'Read more'
    assert data['completed'] is True

    # Verify the todo was updated in the database
    updated_todo = test_db.query(Todo).filter_by(id=todo.id).first()
    assert updated_todo.task == 'Read more'
    assert updated_todo.completed is True


def test_delete_todo(test_client: FlaskClient, test_db: Session) -> None:
    """
    Test case to verify deleting a todo item.
    """
    # Add a todo to the database for testing
    todo = Todo(task='Clean the house')
    test_db.add(todo)
    test_db.commit()

    response = test_client.delete(f'/todos/{todo.id}')
    assert response.status_code == 204  # No Content (successful deletion)
    assert response.data == b'' # Verify empty response body

    # Verify the todo was deleted from the database
    deleted_todo = test_db.query(Todo).filter_by(id=todo.id).first()
    assert deleted_todo is None

def test_invalid_input_add_todo(test_client: FlaskClient) -> None:
    """
    Test case to verify handling of invalid input when adding a todo item.
    """
    response = test_client.post('/todos', json={})  # Missing 'task'
    assert response.status_code == 400  # Bad Request
    data = response.get_json()
    assert 'message' in data


def test_invalid_input_update_todo(test_client: FlaskClient, test_db: Session) -> None:
    """
    Test case to verify handling of invalid input when updating a todo item.
    """
    # Add a todo to the database for testing
    todo = Todo(task='Something')
    test_db.add(todo)
    test_db.commit()

    response = test_client.put(f'/todos/{todo.id}', json={'task': 123})  # Invalid task type
    assert response.status_code == 400  # Bad Request
    data = response.get_json()
    assert 'message' in data
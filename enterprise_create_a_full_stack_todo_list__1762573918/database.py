import sqlite3
from typing import Optional, List, Tuple, Union
import os

DATABASE_PATH = os.environ.get("DATABASE_PATH", "todo.db")  # Get from env for configuration

def create_connection(db_path: str = DATABASE_PATH) -> Optional[sqlite3.Connection]:
    """
    Establishes a connection to the SQLite database.

    Args:
        db_path: The path to the database file.  Defaults to DATABASE_PATH.

    Returns:
        A database connection object, or None if the connection fails.
    """
    conn: Optional[sqlite3.Connection] = None
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to the database: {e}")  # Log the error
        return None


def create_table(conn: sqlite3.Connection) -> bool:
    """
    Creates the 'todos' table if it doesn't already exist.

    Args:
        conn: The database connection object.

    Returns:
        True if the table was created or already exists, False if an error occurred.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")  # Log the error
        return False


def add_todo(conn: sqlite3.Connection, task: str) -> Optional[int]:
    """
    Adds a new todo task to the database.

    Args:
        conn: The database connection object.
        task: The text of the todo task.

    Returns:
        The ID of the newly inserted todo, or None if an error occurred.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO todos (task) VALUES (?)", (task,)
        )  # Use parameterized query to prevent SQL injection
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error adding todo: {e}")  # Log the error
        return None


def get_all_todos(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    """
    Retrieves all todos from the database.

    Args:
        conn: The database connection object.

    Returns:
        A list of sqlite3.Row objects, each representing a todo.  Returns an empty list if an error occurs.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM todos")
        todos = cursor.fetchall()
        return list(todos)  # Ensure return type is a List[sqlite3.Row]
    except sqlite3.Error as e:
        print(f"Error getting all todos: {e}")  # Log the error
        return []


def get_todo_by_id(conn: sqlite3.Connection, todo_id: int) -> Optional[sqlite3.Row]:
    """
    Retrieves a specific todo from the database by its ID.

    Args:
        conn: The database connection object.
        todo_id: The ID of the todo to retrieve.

    Returns:
        An sqlite3.Row object representing the todo, or None if not found or an error occurred.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        todo = cursor.fetchone()
        return todo
    except sqlite3.Error as e:
        print(f"Error getting todo by ID: {e}")  # Log the error
        return None


def update_todo(conn: sqlite3.Connection, todo_id: int, task: str, completed: bool) -> bool:
    """
    Updates an existing todo in the database.

    Args:
        conn: The database connection object.
        todo_id: The ID of the todo to update.
        task: The new text of the todo task.
        completed: The new completion status of the todo.

    Returns:
        True if the todo was updated successfully, False otherwise.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE todos SET task = ?, completed = ? WHERE id = ?", (task, completed, todo_id)
        )  # Use parameterized query
        conn.commit()
        return cursor.rowcount > 0  # Check if any rows were updated
    except sqlite3.Error as e:
        print(f"Error updating todo: {e}")  # Log the error
        return False


def delete_todo(conn: sqlite3.Connection, todo_id: int) -> bool:
    """
    Deletes a todo from the database.

    Args:
        conn: The database connection object.
        todo_id: The ID of the todo to delete.

    Returns:
        True if the todo was deleted successfully, False otherwise.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,)) # Use parameterized query
        conn.commit()
        return cursor.rowcount > 0  # Check if any rows were deleted
    except sqlite3.Error as e:
        print(f"Error deleting todo: {e}")  # Log the error
        return False


def mark_complete(conn: sqlite3.Connection, todo_id: int) -> bool:
    """
    Marks a todo item as complete in the database.

    Args:
        conn: The database connection object.
        todo_id: The ID of the todo item to mark as complete.

    Returns:
        True if the todo item was successfully marked as complete, False otherwise.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE todos SET completed = 1 WHERE id = ?", (todo_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error marking todo as complete: {e}")
        return False


def close_connection(conn: Optional[sqlite3.Connection]) -> None:
    """
    Closes the database connection.

    Args:
        conn: The database connection object.
    """
    if conn:
        try:
            conn.close()
        except sqlite3.Error as e:
            print(f"Error closing connection: {e}")

if __name__ == '__main__':
    # Example usage (for testing)
    conn = create_connection()
    if conn:
        create_table(conn)

        # Add a new todo
        new_todo_id = add_todo(conn, "Learn Flask")
        if new_todo_id:
            print(f"New todo added with ID: {new_todo_id}")

        # Get all todos
        all_todos = get_all_todos(conn)
        print("All Todos:")
        for todo in all_todos:
            print(f"ID: {todo['id']}, Task: {todo['task']}, Completed: {todo['completed']}")

        # Update a todo
        if all_todos:
            first_todo_id = all_todos[0]['id']
            if update_todo(conn, first_todo_id, "Learn Flask - Updated!", True):
                print(f"Todo with ID {first_todo_id} updated successfully.")

        #Get todo by id
        if all_todos:
            first_todo_id = all_todos[0]['id']
            todo = get_todo_by_id(conn, first_todo_id)
            if todo:
                print(f"Todo with ID {first_todo_id}: Task: {todo['task']}, Completed: {todo['completed']}")

        # Mark a todo as complete
        if all_todos:
            first_todo_id = all_todos[0]['id']
            if mark_complete(conn, first_todo_id):
                print(f"Todo with ID {first_todo_id} marked as complete.")
            else:
                 print(f"Failed to mark todo with ID {first_todo_id} as complete.")


        # Delete a todo
        if all_todos:
            first_todo_id = all_todos[0]['id']
            if delete_todo(conn, first_todo_id):
                print(f"Todo with ID {first_todo_id} deleted successfully.")

        close_connection(conn)
    else:
        print("Failed to connect to the database.")
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from typing import Optional

db = SQLAlchemy()


class Todo(db.Model):
    """
    Represents a Todo item in the database.
    """
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)  # Allow longer descriptions
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __init__(self, title: str, description: Optional[str] = None, completed: bool = False):
        """
        Initializes a new Todo item.

        Args:
            title: The title of the todo (required).
            description: An optional description for the todo.
            completed: A boolean indicating if the todo is completed (defaults to False).
        Raises:
            TypeError: If title is not a string or is empty.
        """
        if not isinstance(title, str) or not title:
            raise TypeError("Title must be a non-empty string")

        if description is not None and not isinstance(description, str):
            raise TypeError("Description must be a string or None")

        if not isinstance(completed, bool):
            raise TypeError("Completed must be a boolean")


        self.title = title
        self.description = description
        self.completed = completed

    def __repr__(self) -> str:
        """
        Returns a string representation of the Todo object.

        Returns:
            A string representation of the Todo object.
        """
        return f"<Todo(id={self.id}, title='{self.title}', completed={self.completed})>"

    def to_dict(self) -> dict:
        """
        Converts the Todo object to a dictionary.

        Returns:
            A dictionary representation of the Todo object.
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Todo":
        """
        Creates a Todo object from a dictionary.

        Args:
            data: A dictionary containing the Todo data.

        Returns:
            A Todo object.
        Raises:
            TypeError: if the data dictionary has the incorrect fields or datatypes.
            ValueError: if required fields are missing from the dictionary.
        """

        try:
            title = data['title']
            description = data.get('description') #Handles optional description
            completed = data.get('completed', False) # Handles optional completed

            return cls(title=title, description=description, completed=completed)
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}") from e
        except TypeError as e:
            raise TypeError(f"Invalid data type in dictionary: {e}") from e
        except Exception as e:
            raise Exception(f"Error creating Todo from dictionary: {e}") from e
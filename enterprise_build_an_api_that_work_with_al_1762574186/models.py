from typing import Optional, List, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field, validator, ValidationError
import secrets
import hashlib


class User(BaseModel):
    """
    Represents a user of the social media management API.
    """
    user_id: str = Field(default_factory=lambda: secrets.token_hex(16), description="Unique identifier for the user.")
    username: str = Field(..., min_length=3, max_length=50, description="Username for the user.")
    hashed_password: str = Field(..., description="Hashed password of the user.") # Store only the hash
    email: str = Field(..., description="Email address of the user.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the user was created.")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the user was last updated.")
    is_active: bool = Field(default=True, description="Indicates if the user account is active.")

    @validator("email")
    def validate_email(cls, email: str) -> str:
        """
        Validates the email format.  A more robust solution using a library like `email_validator` is recommended.
        """
        if "@" not in email or "." not in email:
            raise ValueError("Invalid email format.")
        return email

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes the password using SHA-256 with a salt."""
        salt = secrets.token_hex(16)
        salted_password = password + salt
        hashed_password = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
        return f"{salt}${hashed_password}"

    def verify_password(self, password: str) -> bool:
        """Verifies a password against the stored hash."""
        salt, hashed_password = self.hashed_password.split("$", 1)
        salted_password = password + salt
        new_hashed_password = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
        return new_hashed_password == hashed_password
    
    class Config:
        """Pydantic configuration options."""
        orm_mode = True  # Enable ORM mode for database integration (if applicable)


class SocialMediaAccount(BaseModel):
    """
    Represents a social media account linked to a user.
    """
    account_id: str = Field(default_factory=lambda: secrets.token_hex(16), description="Unique identifier for the social media account.")
    user_id: str = Field(..., description="Foreign key referencing the user owning the account.")
    platform: str = Field(..., description="The social media platform (e.g., 'Twitter', 'Facebook', 'Instagram').")
    account_name: str = Field(..., description="The username or account name on the social media platform.")
    access_token: str = Field(..., description="Access token for authenticating with the social media platform.")
    refresh_token: Optional[str] = Field(None, description="Refresh token (if applicable) for obtaining new access tokens.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the account was linked.")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the account was last updated.")

    class Config:
        """Pydantic configuration options."""
        orm_mode = True  # Enable ORM mode for database integration (if applicable)


class Content(BaseModel):
    """
    Represents content to be posted on social media.
    """
    content_id: str = Field(default_factory=lambda: secrets.token_hex(16), description="Unique identifier for the content.")
    user_id: str = Field(..., description="Foreign key referencing the user who created the content.")
    text: str = Field(..., description="The text content of the post.")
    media_url: Optional[str] = Field(None, description="Optional URL for associated media (image or video).")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the content was created.")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the content was last updated.")

    class Config:
        """Pydantic configuration options."""
        orm_mode = True  # Enable ORM mode for database integration (if applicable)


class ScheduledPost(BaseModel):
    """
    Represents a scheduled social media post.
    """
    post_id: str = Field(default_factory=lambda: secrets.token_hex(16), description="Unique identifier for the scheduled post.")
    content_id: str = Field(..., description="Foreign key referencing the content to be posted.")
    account_id: str = Field(..., description="Foreign key referencing the social media account to post to.")
    scheduled_time: datetime = Field(..., description="The date and time when the post should be published.")
    status: str = Field(default="pending", description="The status of the post (e.g., 'pending', 'posted', 'failed').")
    posted_at: Optional[datetime] = Field(None, description="Timestamp when the post was actually published.")
    error_message: Optional[str] = Field(None, description="Error message if the post failed.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the scheduled post was created.")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the scheduled post was last updated.")

    class Config:
        """Pydantic configuration options."""
        orm_mode = True  # Enable ORM mode for database integration (if applicable)


class APIError(BaseModel):
    """
    Represents a generic API error response.
    """
    error_code: int = Field(..., description="Error code indicating the type of error.")
    message: str = Field(..., description="A human-readable error message.")
    details: Optional[Dict[str, Any]] = Field(None, description="Optional details about the error.")

    class Config:
        """Pydantic configuration options."""
        schema_extra = {
            "example": {
                "error_code": 400,
                "message": "Invalid request data.",
                "details": {"field": "username", "error": "Username must be at least 3 characters."}
            }
        }
from typing import Optional, List, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field, validator

# Security: Consider using UUIDs instead of sequential integers for IDs if security is a concern
#            to prevent enumeration attacks.


class SocialMediaPlatform(BaseModel):
    """
    Represents a social media platform.
    """
    platform_id: int = Field(..., description="Unique identifier for the platform.")
    name: str = Field(..., description="Name of the platform (e.g., Facebook, Twitter).")
    api_endpoint: str = Field(..., description="API endpoint for the platform.")
    # Security: Store API keys securely (e.g., using environment variables, secrets management).
    api_key: str = Field(..., description="API Key for the platform.  (DO NOT STORE DIRECTLY)")


class User(BaseModel):
    """
    Represents a user of the system.
    """
    user_id: int = Field(..., description="Unique identifier for the user.")
    username: str = Field(..., description="Username of the user.")
    email: str = Field(..., description="Email address of the user.")
    # Security: Hashed password should be stored, not plain text.  Consider using a secure hashing library like bcrypt.
    hashed_password: str = Field(..., description="Hashed password of the user. (DO NOT STORE PLAIN TEXT)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of user creation.")


class SocialMediaAccount(BaseModel):
    """
    Represents a user's connected social media account.
    """
    account_id: int = Field(..., description="Unique identifier for the account.")
    user_id: int = Field(..., description="Foreign key referencing the user owning the account.")
    platform_id: int = Field(..., description="Foreign key referencing the social media platform.")
    account_username: str = Field(..., description="Username of the account on the social media platform.")
    # Security: OAuth tokens should be stored securely (e.g., encrypted in the database).
    oauth_token: str = Field(..., description="OAuth token for the account. (STORE SECURELY)")


class Content(BaseModel):
    """
    Represents the content to be posted.
    """
    content_id: int = Field(..., description="Unique identifier for the content.")
    user_id: int = Field(..., description="Foreign key referencing the user who created the content.")
    text: str = Field(..., description="Text of the content.")
    image_url: Optional[str] = Field(None, description="Optional URL of an image to be posted.")
    video_url: Optional[str] = Field(None, description="Optional URL of a video to be posted.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of content creation.")

    @validator("image_url", "video_url")
    def validate_url(cls, value):
        """
        Validates that the URL is a valid URL format.
        """
        if value:
            # Consider adding a more robust URL validation library like `validators`.
            if not value.startswith(("http://", "https://")):
                raise ValueError("URL must start with http:// or https://")
        return value


class Post(BaseModel):
    """
    Represents a scheduled or executed post.
    """
    post_id: int = Field(..., description="Unique identifier for the post.")
    content_id: int = Field(..., description="Foreign key referencing the content to be posted.")
    account_id: int = Field(..., description="Foreign key referencing the social media account to post to.")
    scheduled_at: Optional[datetime] = Field(None, description="Timestamp when the post is scheduled to be posted.")
    posted_at: Optional[datetime] = Field(None, description="Timestamp when the post was actually posted.")
    status: str = Field("pending", description="Status of the post (e.g., pending, posted, failed).")
    error_message: Optional[str] = Field(None, description="Error message if the post failed.")

    @validator("status")
    def validate_status(cls, value):
        """
        Validates that the status is one of the allowed values.
        """
        allowed_statuses = ["pending", "posted", "failed", "scheduled"]
        if value not in allowed_statuses:
            raise ValueError(f"Status must be one of: {allowed_statuses}")
        return value


class ContentGenerationRequest(BaseModel):
    """
    Represents a request for content generation.
    """
    topic: str = Field(..., description="Topic for content generation.")
    keywords: List[str] = Field(..., description="Keywords to guide content generation.")
    style: str = Field("informative", description="Desired style of the content.")
    length: str = Field("short", description="Desired length of the content (e.g., short, medium, long).")

class ContentGenerationResponse(BaseModel):
    """
    Represents the response from the content generation service.
    """
    generated_text: str = Field(..., description="The generated content text.")
    suggested_hashtags: List[str] = Field(default_factory=list, description="Suggested hashtags for the content.")
    # Consider adding confidence scores or quality metrics to the response.
    quality_score: Optional[float] = Field(None, description="A score representing the quality of the generated content.")


class APIError(BaseModel):
    """
    Represents a generic API error.
    """
    error_code: int = Field(..., description="Error code.")
    error_message: str = Field(..., description="Error message.")
    details: Optional[Dict[str, Any]] = Field(None, description="Optional error details.")
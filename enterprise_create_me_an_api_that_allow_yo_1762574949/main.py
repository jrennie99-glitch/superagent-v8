import os
import logging
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader, APIKeyQuery
from pydantic import BaseModel, Field

# Import social media posting logic (replace with actual implementation)
from .social_media_poster import post_to_social_media  # Assuming a separate module

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize FastAPI app
app = FastAPI(
    title="Social Media Auto-Poster API",
    description="An API for automating content posting to multiple social media platforms.",
    version="1.0.0",
    docs_url="/docs",  # Enable Swagger UI documentation
    redoc_url="/redoc",  # Enable ReDoc documentation
)

# API Key Authentication
API_KEY_NAME = "X-API-Key"
API_KEY = os.environ.get("API_KEY", "your_default_api_key")  # Use environment variable
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=True)


async def get_api_key(
    api_key_header: str = Security(api_key_header, auto_error=True),
    api_key_query: str = Security(api_key_query, auto_error=True),
) -> str:
    """
    Authenticates the API key provided in the header or query parameters.

    Args:
        api_key_header: API key from the header.
        api_key_query: API key from the query parameters.

    Returns:
        The API key if it's valid.

    Raises:
        HTTPException: If the API key is invalid.
    """
    if api_key_header == API_KEY:
        return api_key_header
    elif api_key_query == API_KEY:
        return api_key_query
    else:
        logging.warning("Invalid API key provided.")
        raise HTTPException(status_code=403, detail="Invalid API Key")


# Request Body Model
class PostContent(BaseModel):
    """
    Request body for posting content.
    """

    content: str = Field(
        ...,
        title="Content",
        description="The content to be posted on social media.",
        min_length=1,
    )
    platforms: Optional[list[str]] = Field(
        None,
        title="Platforms",
        description="List of social media platforms to post to (e.g., 'facebook', 'twitter'). If None, posts to all configured platforms.",
    )

    # Example content for documentation
    class Config:
        schema_extra = {
            "example": {
                "content": "Check out my new blog post!",
                "platforms": ["facebook", "twitter"],
            }
        }


# Response Model
class PostResponse(BaseModel):
    """
    Response after attempting to post content.
    """

    success: bool = Field(
        ..., title="Success", description="Indicates whether the post was successful."
    )
    message: str = Field(
        ...,
        title="Message",
        description="A message indicating the outcome of the post attempt.",
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        title="Details",
        description="Optional details about the post attempt, e.g., errors from specific platforms.",
    )


@app.post(
    "/post",
    response_model=PostResponse,
    summary="Post content to social media platforms",
    description="Posts the given content to one or more social media platforms. Requires a valid API key.",
)
async def post_endpoint(
    post_data: PostContent, api_key: str = Depends(get_api_key)
) -> PostResponse:
    """
    API endpoint for posting content to social media.

    Args:
        post_data: The content to be posted and the target platforms.
        api_key: The API key used for authentication (automatically handled by Depends).

    Returns:
        A PostResponse indicating the success or failure of the post attempt.

    Raises:
        HTTPException: If any error occurs during the posting process.
    """
    try:
        # Call the social media posting function (from social_media_poster.py)
        result = await post_to_social_media(post_data.content, post_data.platforms)  # type: ignore
        logging.info(f"Content posted successfully. Result: {result}")

        return PostResponse(
            success=True, message="Content posted successfully.", details=result
        )

    except Exception as e:
        logging.exception("Error posting content to social media.")
        raise HTTPException(status_code=500, detail=str(e))
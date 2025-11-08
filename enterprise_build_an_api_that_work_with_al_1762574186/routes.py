from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

# Import necessary models and services
from .models import UserCreate, UserRead, SocialMediaPost, PostResponse
from .services import user_service, auth_service, social_media_service  # Assuming these services exist
from .dependencies import get_current_user  # Assuming this dependency exists

# Create an APIRouter instance
router = APIRouter()


# Authentication endpoints
@router.post("/token", response_model=Dict[str, str], summary="Get access token using username and password")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Endpoint to obtain an access token.  Requires valid username and password.

    Args:
        form_data (OAuth2PasswordRequestForm): Username and password.

    Returns:
        dict: A dictionary containing the access token and token type.

    Raises:
        HTTPException: If authentication fails.
    """
    try:
        access_token = await auth_service.authenticate_user(
            form_data.username, form_data.password
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.post("/users/", response_model=UserRead, status_code=status.HTTP_201_CREATED, summary="Create a new user")
async def create_user(user: UserCreate) -> Any:
    """
    Endpoint to create a new user.

    Args:
        user (UserCreate): User creation data.

    Returns:
        UserRead: The created user's data.

    Raises:
        HTTPException: If user creation fails (e.g., username already exists).
    """
    try:
        created_user = await user_service.create_user(user)
        return created_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        ) from e


# User endpoint (requires authentication)
@router.get("/users/me/", response_model=UserRead, summary="Get the current user's information")
async def read_users_me(current_user: UserRead = Depends(get_current_user)) -> Any:
    """
    Endpoint to retrieve the current authenticated user's information.

    Args:
        current_user (UserRead):  The authenticated user, injected as a dependency.

    Returns:
        UserRead: The current user's data.
    """
    return current_user


# Social Media Posting Endpoints (requires authentication)
@router.post("/posts/", response_model=PostResponse, summary="Create and post to social media")
async def create_social_media_post(
    post: SocialMediaPost, current_user: UserRead = Depends(get_current_user)
) -> Any:
    """
    Endpoint to create and post content to connected social media accounts.

    Args:
        post (SocialMediaPost): The content to be posted.
        current_user (UserRead): The authenticated user.

    Returns:
        PostResponse: The result of the social media posting.

    Raises:
        HTTPException: If posting fails to any of the social media platforms.
    """
    try:
        post_result = await social_media_service.post_to_social_media(
            post, current_user
        )  #  Delegate to the social_media_service
        return post_result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        # Log the full error for debugging purposes
        print(f"Error posting to social media: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to post to social media: {e}",
        ) from e


@router.get("/posts/", response_model=List[PostResponse], summary="Retrieve recent social media posts")
async def get_recent_posts(current_user: UserRead = Depends(get_current_user)) -> Any:
    """
    Endpoint to retrieve recent social media posts made by the user.

    Args:
        current_user (UserRead): The authenticated user.

    Returns:
        List[PostResponse]: A list of recent social media posts.

    Raises:
        HTTPException: If retrieving posts fails.
    """
    try:
        posts = await social_media_service.get_user_posts(current_user)
        return posts
    except Exception as e:
        # Log the full error for debugging purposes
        print(f"Error retrieving posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve posts: {e}",
        ) from e
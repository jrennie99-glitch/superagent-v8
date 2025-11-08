import os
import logging
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader, APIKey
from fastapi.exceptions import RequestValidationError

# Import routes from other modules
from routes import auth, posts, users # hypothetical routes module

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Define API keys and security headers
API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

# Initialize FastAPI app
app = FastAPI(
    title="Social Media Automation API",
    description="API for creating and automatically posting content to various social media platforms.",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Configure CORS (Cross-Origin Resource Sharing)
origins = [
    "http://localhost",
    "http://localhost:8080", # Example frontend URL
    "*", #REMOVE IN PRODUCTION - this is for development only.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security: API Key Dependency
async def get_api_key(api_key_header: str = Depends(api_key_header)) -> str:
    """
    Dependency to validate the API Key.

    Args:
        api_key_header: The API key provided in the header.

    Returns:
        The API key if valid.

    Raises:
        HTTPException: If the API key is invalid.
    """
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key",
    )


# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom exception handler for RequestValidationError.

    Args:
        request: The request object.
        exc: The RequestValidationError exception.

    Returns:
        A JSONResponse containing the validation error details.
    """
    logging.error(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


# Register routes from other modules
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(posts.router, prefix="/api/posts", tags=["Posts"], dependencies=[Depends(get_api_key)])
app.include_router(users.router, prefix="/api/users", tags=["Users"], dependencies=[Depends(get_api_key)])


# Root endpoint
@app.get("/api", tags=["Root"])
async def read_root() -> Dict[str, str]:
    """
    Root endpoint for the API.

    Returns:
        A simple greeting.
    """
    return {"message": "Welcome to the Social Media Automation API!"}


# Error handling for unexpected exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    General exception handler for unhandled exceptions.

    Args:
        request: The request object.
        exc: The Exception object.

    Returns:
        A JSONResponse with a generic error message.
    """
    logging.exception(f"An unexpected error occurred: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please check the server logs."},
    )



if __name__ == "__main__":
    # Example of how to run the app using uvicorn (for development)
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000) # nosec #B104: Possible binding to all interfaces
import unittest
import json
from typing import Dict, Any
from unittest.mock import patch
from urllib.parse import quote

from fastapi.testclient import TestClient

from .main import app  # Assuming your main file is named main.py
# Import any necessary models or schemas from your main file
from .schemas import Post  # Example, adjust as needed
# from .database import SessionLocal, engine, Base # Adjust based on your actual imports
# Base.metadata.create_all(bind=engine) # Create database tables (adjust based on your setup)

class TestSocialMediaAPI(unittest.TestCase):
    """
    Test suite for the social media API.
    """

    def setUp(self):
        """
        Setup method to initialize the TestClient before each test.
        """
        self.client = TestClient(app)
        # Consider using an in-memory database or a test database
        # For example, if using SQLAlchemy:
        # self.db = SessionLocal()
        # Base.metadata.create_all(bind=engine)

    def tearDown(self):
        """
        Teardown method to clean up resources after each test.
        """
        # if hasattr(self, 'db'):
        #     self.db.close()
        pass  # Add any cleanup logic here if needed


    def test_create_post(self):
        """
        Test case for creating a new post.
        """
        payload: Dict[str, Any] = {
            "content": "Test post content",
            "platforms": ["twitter", "facebook"]
        }
        response = self.client.post("/posts/", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["content"], payload["content"])
        self.assertEqual(data["platforms"], payload["platforms"])

        # Example using the Post schema, after ensuring that the response matches
        # try:
        #     post = Post(**data) # Validate data against your Pydantic model
        # except ValidationError as e:
        #     self.fail(f"Response does not conform to Post schema: {e}")



    def test_get_post_by_id(self):
        """
        Test case for retrieving a post by its ID.
        """
        # First create a post
        payload: Dict[str, Any] = {
            "content": "Test post content for retrieval",
            "platforms": ["twitter"]
        }
        create_response = self.client.post("/posts/", json=payload)
        self.assertEqual(create_response.status_code, 201)
        created_data = create_response.json()
        post_id: int = created_data["id"]

        # Then retrieve the post
        response = self.client.get(f"/posts/{post_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], post_id)
        self.assertEqual(data["content"], payload["content"])
        self.assertEqual(data["platforms"], payload["platforms"])

    def test_get_post_by_id_not_found(self):
        """
        Test case for retrieving a post with a non-existent ID.
        """
        response = self.client.get("/posts/9999")  # Assuming 9999 is a non-existent ID
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["detail"], "Post not found")

    def test_update_post(self):
        """
        Test case for updating an existing post.
        """
        # Create a post first
        payload: Dict[str, Any] = {
            "content": "Original content",
            "platforms": ["twitter"]
        }
        create_response = self.client.post("/posts/", json=payload)
        self.assertEqual(create_response.status_code, 201)
        created_data = create_response.json()
        post_id: int = created_data["id"]

        # Update the post
        update_payload: Dict[str, Any] = {
            "content": "Updated content",
            "platforms": ["facebook"]
        }
        response = self.client.put(f"/posts/{post_id}", json=update_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], post_id)
        self.assertEqual(data["content"], update_payload["content"])
        self.assertEqual(data["platforms"], update_payload["platforms"])

    def test_delete_post(self):
        """
        Test case for deleting a post.
        """
        # Create a post first
        payload: Dict[str, Any] = {
            "content": "Content to delete",
            "platforms": ["instagram"]
        }
        create_response = self.client.post("/posts/", json=payload)
        self.assertEqual(create_response.status_code, 201)
        created_data = create_response.json()
        post_id: int = created_data["id"]

        # Delete the post
        response = self.client.delete(f"/posts/{post_id}")
        self.assertEqual(response.status_code, 204)

        # Verify the post is deleted
        get_response = self.client.get(f"/posts/{post_id}")
        self.assertEqual(get_response.status_code, 404)

    def test_get_all_posts(self):
        """
        Test case for retrieving all posts.
        """
        # Add some dummy posts if needed.
        # For example, clear the database if using one.
        # Or add a few posts here so they can be retrieved.

        response = self.client.get("/posts/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)  # Make sure it's a list
        # Add more specific assertions based on your data structure

    def test_create_post_validation_error(self):
        """
        Test case for handling validation errors when creating a post.
        """
        payload: Dict[str, Any] = {
            "content": "",  # Invalid content
            "platforms": ["invalid-platform"] #Invalid platform (if you have platform validation)
        }
        response = self.client.post("/posts/", json=payload)
        self.assertEqual(response.status_code, 422)  # Unprocessable Entity

        data = response.json()
        self.assertIn("detail", data) #Error details exist
        self.assertIsInstance(data["detail"], list) # Make sure detail is a list of errors

    def test_create_post_with_xss(self):
        """
        Test case to verify that the API handles Cross-Site Scripting (XSS) attempts.
        """
        payload: Dict[str, Any] = {
            "content": "<script>alert('XSS')</script>",  # Attempted XSS
            "platforms": ["twitter"]
        }
        response = self.client.post("/posts/", json=payload)
        self.assertEqual(response.status_code, 201) # Or a code indicating failure to process the post
        data = response.json()

        # Check if the script tag was sanitized (e.g., stripped or encoded)
        # Assert that "script" or "<script>" is NOT present in the stored content
        if "content" in data:
            self.assertNotIn("script", data["content"].lower())
            self.assertNotIn("<script>", data["content"].lower())


    # Add more test cases for:
    # - Handling invalid platform names.
    # - Testing rate limiting (if implemented).
    # - Testing authentication/authorization (if implemented).
    # - Validating input data types (e.g., content length).
    # - Testing error responses more thoroughly.
    # - Testing different HTTP methods (e.g., HEAD, OPTIONS).
    # - Testing for proper logging.
    # - Testing concurrency if applicable.


if __name__ == "__main__":
    unittest.main()
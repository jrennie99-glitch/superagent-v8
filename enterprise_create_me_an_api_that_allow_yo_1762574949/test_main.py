import unittest
import json
from typing import Dict, Any
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import status
from main import app  # Assuming your main file is named main.py

# Create a test client for the FastAPI app
client = TestClient(app)


class TestMainAPI(unittest.TestCase):
    """
    Test suite for the social media auto-posting API.
    """

    def setUp(self):
        """
        Set up for each test case.  Consider initializing test-specific configurations here.
        """
        pass  # No setup required for this example, but can be extended.

    def tearDown(self):
        """
        Tear down after each test case.  Clean up any resources.
        """
        pass  # No teardown required for this example, but can be extended.

    @patch("main.post_to_social_media")  # Replace with actual function name
    def test_auto_post_success(self, mock_post_to_social_media):
        """
        Test the auto-posting endpoint with a successful scenario.
        """
        # Mock the external function to avoid actual social media posting during testing.
        mock_post_to_social_media.return_value = {"status": "success", "message": "Posted successfully!"}

        # Define the request payload (example)
        payload: Dict[str, Any] = {
            "content": "This is a test post.",
            "platforms": ["facebook", "twitter"],
        }

        # Send a POST request to the endpoint
        response = client.post("/autopost/", json=payload)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert the response content
        expected_response: Dict[str, str] = {"status": "success", "message": "Posted successfully!"}
        self.assertEqual(response.json(), expected_response)

        # Assert that the mocked function was called with the correct arguments.
        mock_post_to_social_media.assert_called_once_with(payload["content"], payload["platforms"])

    @patch("main.post_to_social_media")  # Replace with actual function name
    def test_auto_post_platform_failure(self, mock_post_to_social_media):
        """
        Test the auto-posting endpoint when posting to one or more platforms fails.
        """
        # Mock the external function to simulate a failure on a specific platform.
        mock_post_to_social_media.return_value = {"status": "failure", "message": "Failed to post to Twitter."}

        # Define the request payload (example)
        payload: Dict[str, Any] = {
            "content": "This is a test post that will fail.",
            "platforms": ["facebook", "twitter"],
        }

        # Send a POST request to the endpoint
        response = client.post("/autopost/", json=payload)

        # Assert the response status code (consider a different status code for partial failure)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR) # Or HTTP_207_MULTI_STATUS

        # Assert the response content
        expected_response: Dict[str, str] = {"status": "failure", "message": "Failed to post to Twitter."}
        self.assertEqual(response.json(), expected_response)

        # Assert that the mocked function was called with the correct arguments.
        mock_post_to_social_media.assert_called_once_with(payload["content"], payload["platforms"])

    def test_auto_post_invalid_input(self):
        """
        Test the auto-posting endpoint with invalid input data.
        """
        # Define an invalid request payload (e.g., missing required fields)
        payload: Dict[str, Any] = {"content": ""}  # Missing "platforms"

        # Send a POST request to the endpoint
        response = client.post("/autopost/", json=payload)

        # Assert the response status code (should be 422 for validation errors)
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

        # Assert that the response content contains validation error details.
        self.assertIn("detail", response.json())

    def test_auto_post_empty_content(self):
        """
        Test the auto-posting endpoint with empty content.
        """
        # Define a request payload with empty content
        payload: Dict[str, Any] = {"content": "", "platforms": ["facebook"]}

        # Send a POST request to the endpoint
        response = client.post("/autopost/", json=payload)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("detail", response.json())

    def test_health_check(self):
        """
        Test the health check endpoint.
        """
        response = client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_auto_post_invalid_platform(self):
        """
        Test the auto-posting endpoint with an invalid social media platform.
        """
        payload: Dict[str, Any] = {
            "content": "Test content",
            "platforms": ["invalid_platform"],
        }

        response = client.post("/autopost/", json=payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid social media platform", response.json()["detail"])
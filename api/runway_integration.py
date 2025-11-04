"""
Runway ML API Integration for AI Video Generation
Supports Gen-3 Alpha (latest model) for text-to-video and image-to-video
"""

import os
import requests
import time
from typing import Optional, Dict, Any

class RunwayVideoGenerator:
    """
    Runway ML Gen-3 Alpha Integration
    Industry-leading AI video generation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('RUNWAY_API_KEY')
        self.base_url = "https://api.dev.runwayml.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-06"
        }
    
    def generate_video_from_text(
        self,
        prompt: str,
        duration: int = 5,
        aspect_ratio: str = "16:9",
        model: str = "gen3a_turbo"
    ) -> Dict[str, Any]:
        """
        Generate video from text prompt using Gen-3 Alpha
        
        Args:
            prompt: Text description of the video to generate
            duration: Video duration in seconds (5 or 10)
            aspect_ratio: Video aspect ratio (16:9, 9:16, 4:3, 3:4, 1:1)
            model: Model to use (gen3a_turbo or gen3a)
        
        Returns:
            Dict with task_id and status
        """
        
        if not self.api_key:
            return {
                "success": False,
                "error": "RUNWAY_API_KEY not set. Get your API key from https://app.runwayml.com/settings/api-keys"
            }
        
        try:
            # Create generation task with correct Runway API format
            payload = {
                "promptText": prompt,
                "model": model,
                "duration": duration,
                "aspectRatio": aspect_ratio
            }
            
            response = requests.post(
                f"{self.base_url}/image_to_video",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            # Runway returns 202 Accepted for queued tasks
            if response.status_code in [200, 201, 202]:
                data = response.json()
                return {
                    "success": True,
                    "task_id": data.get("id"),
                    "status": "processing",
                    "message": f"Video generation started! Task ID: {data.get('id')}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Runway API error ({response.status_code}): {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error generating video: {str(e)}"
            }
    
    def generate_video_from_image(
        self,
        image_url: str,
        prompt: str,
        aspect_ratio: str = "16:9",
        model: str = "gen3a_turbo"
    ) -> Dict[str, Any]:
        """
        Generate video from image + text prompt (Image-to-Video)
        
        Args:
            image_url: URL of the source image
            prompt: Text description for the video motion/action
            aspect_ratio: Video aspect ratio (16:9, 9:16, etc.)
            model: Model to use
        
        Returns:
            Dict with task_id and status
        """
        
        if not self.api_key:
            return {
                "success": False,
                "error": "RUNWAY_API_KEY not set"
            }
        
        try:
            payload = {
                "promptText": prompt,
                "promptImage": image_url,
                "model": model,
                "aspectRatio": aspect_ratio
            }
            
            response = requests.post(
                f"{self.base_url}/image_to_video",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            # Runway returns 202 Accepted for queued tasks
            if response.status_code in [200, 201, 202]:
                data = response.json()
                return {
                    "success": True,
                    "task_id": data.get("id"),
                    "status": "processing",
                    "message": f"Image-to-video generation started! Task ID: {data.get('id')}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Runway API error ({response.status_code}): {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }
    
    def check_status(self, task_id: str) -> Dict[str, Any]:
        """
        Check the status of a video generation task
        
        Args:
            task_id: The task ID returned from generation
        
        Returns:
            Dict with status and video_url if completed
        """
        
        if not self.api_key:
            return {"success": False, "error": "API key not set"}
        
        try:
            response = requests.get(
                f"{self.base_url}/tasks/{task_id}",
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "").upper()
                
                result = {
                    "success": True,
                    "task_id": task_id,
                    "status": status.lower()
                }
                
                # Runway returns status as SUCCEEDED, RUNNING, PENDING, FAILED
                if status == "SUCCEEDED":
                    # Output is array of video URLs
                    output = data.get("output", [])
                    if output and len(output) > 0:
                        result["video_url"] = output[0].get("url")
                        result["message"] = "Video generated successfully!"
                    else:
                        result["error"] = "No video URL in output"
                elif status == "FAILED":
                    result["error"] = data.get("failure", "Unknown error")
                elif status in ["RUNNING", "PENDING"]:
                    result["message"] = f"Video generation in progress... ({status.lower()})"
                else:
                    result["message"] = f"Status: {status.lower()}"
                
                return result
            else:
                return {
                    "success": False,
                    "error": f"API error ({response.status_code}): {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error checking status: {str(e)}"
            }
    
    def wait_for_completion(
        self,
        task_id: str,
        max_wait: int = 300,
        poll_interval: int = 10
    ) -> Dict[str, Any]:
        """
        Wait for video generation to complete
        
        Args:
            task_id: Task ID to wait for
            max_wait: Maximum time to wait in seconds
            poll_interval: How often to check status
        
        Returns:
            Final status dict with video_url
        """
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            result = self.check_status(task_id)
            
            if not result.get("success"):
                return result
            
            status = result.get("status")
            
            if status == "succeeded":
                return result
            elif status == "failed":
                return result
            
            time.sleep(poll_interval)
        
        return {
            "success": False,
            "error": "Timeout waiting for video generation"
        }

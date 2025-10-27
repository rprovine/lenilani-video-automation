"""
Google Vertex AI image generation client service.
Handles image generation using Google Vertex AI Imagen 3 (nano-banana) API.
"""

from typing import Optional
import logging
import base64
import httpx
from ..config import settings

logger = logging.getLogger(__name__)


class GoogleImageService:
    """Service for generating images using Google Vertex AI Imagen 3."""

    def __init__(self):
        """Initialize Google Vertex AI client."""
        self.api_key = settings.google_api_key
        self.project_id = settings.google_project_id
        self.region = settings.google_region
        self.base_url = f"https://{self.region}-aiplatform.googleapis.com/v1"

    async def generate_image(
        self,
        prompt: str,
        output_path: Optional[str] = None
    ) -> dict:
        """
        Generate an image from a text prompt using Google's Imagen API.

        Args:
            prompt: Text description of the image to generate
            output_path: Optional local path to save the image

        Returns:
            Dict with image_url or image_data
        """
        try:
            logger.info(f"Generating image with Google Imagen 4: {prompt[:100]}...")

            # Use Google Generative AI API with correct endpoint
            endpoint = "https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict"

            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key  # Correct authentication header
            }

            # Payload for Imagen 4 API
            payload = {
                "instances": [
                    {
                        "prompt": prompt
                    }
                ],
                "parameters": {
                    "sampleCount": 1,
                    "aspectRatio": "16:9",  # Good for blog featured images
                    "safetyFilterLevel": "block_some"
                }
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(endpoint, json=payload, headers=headers)

                # Log response for debugging
                logger.info(f"Google Imagen API response status: {response.status_code}")

                if response.status_code >= 400:
                    error_text = response.text
                    logger.error(f"Google Imagen API error response: {error_text}")

                response.raise_for_status()
                result = response.json()
                logger.info(f"Google Imagen API response keys: {result.keys()}")

            # Extract image data from response
            if "predictions" in result and len(result["predictions"]) > 0:
                prediction = result["predictions"][0]

                # Image is returned as base64
                if "bytesBase64Encoded" in prediction:
                    image_bytes = base64.b64decode(prediction["bytesBase64Encoded"])

                    if output_path:
                        with open(output_path, "wb") as f:
                            f.write(image_bytes)
                        logger.info(f"Saved generated image to {output_path}")

                    return {
                        "success": True,
                        "image_data": image_bytes,
                        "output_path": output_path
                    }
                elif "image" in prediction:
                    # Alternative response format
                    image_bytes = base64.b64decode(prediction["image"])

                    if output_path:
                        with open(output_path, "wb") as f:
                            f.write(image_bytes)
                        logger.info(f"Saved generated image to {output_path}")

                    return {
                        "success": True,
                        "image_data": image_bytes,
                        "output_path": output_path
                    }

            raise Exception("No image data in response")

        except httpx.HTTPStatusError as e:
            error_text = e.response.text
            logger.error(f"Vertex AI HTTP error: {e.response.status_code} - {error_text}")
            if e.response.status_code == 401:
                logger.error("Authentication failed. Check Google Vertex AI API key.")
            elif e.response.status_code == 403:
                logger.error("Forbidden. Verify Imagen API is enabled and permissions are correct.")
            elif e.response.status_code == 404:
                logger.error("Endpoint not found. Check project ID and region.")

            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {error_text}",
                "message": f"Vertex AI error: {e.response.status_code}"
            }

        except Exception as e:
            logger.error(f"Error generating image: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Image generation failed: {str(e)}"
            }

    async def generate_and_upload(
        self,
        prompt: str,
        temp_path: str = "/tmp/generated_image.png"
    ) -> Optional[str]:
        """
        Generate an image and return it ready for upload.

        Args:
            prompt: Text description of the image
            temp_path: Temporary path to save the image

        Returns:
            Path to the generated image file, or None if generation failed
        """
        try:
            result = await self.generate_image(prompt, output_path=temp_path)

            if result.get("success") and result.get("output_path"):
                logger.info(f"Image ready for upload at {result['output_path']}")
                return result["output_path"]
            else:
                logger.warning(f"Image generation unsuccessful: {result.get('message')}")
                return None

        except Exception as e:
            logger.error(f"Error in generate_and_upload: {e}")
            return None


# Global instance
google_image_service = GoogleImageService()

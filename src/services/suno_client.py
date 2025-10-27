"""
Suno AI music generation service.
Generates background music for videos using Suno AI.
"""

import time
import logging
import httpx
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class SunoMusicService:
    """Service for generating music with Suno AI."""

    def __init__(self, base_url: str = "http://localhost:3000", cookie: Optional[str] = None):
        """
        Initialize Suno music service.

        Args:
            base_url: Base URL of suno-api server (default: localhost:3000)
            cookie: Suno account cookie for authentication
        """
        self.base_url = base_url
        self.cookie = cookie

    async def generate_music(
        self,
        prompt: str,
        duration: int = 30,
        output_path: str = "/tmp/suno_music.mp3",
        instrumental: bool = True,
        make_instrumental: bool = True
    ) -> Dict[str, Any]:
        """
        Generate music using Suno AI.

        Args:
            prompt: Description of the music to generate
            duration: Desired duration in seconds (max ~120s)
            output_path: Where to save the generated music
            instrumental: Whether to generate instrumental music
            make_instrumental: Force instrumental (no vocals)

        Returns:
            Dict with success status and file path
        """
        try:
            logger.info(f"Generating Suno music: {prompt}")

            async with httpx.AsyncClient(timeout=300.0) as client:
                # Step 1: Generate music
                generate_url = f"{self.base_url}/api/generate"
                payload = {
                    "prompt": prompt,
                    "make_instrumental": make_instrumental,
                    "wait_audio": False  # Don't wait, we'll poll
                }

                logger.info(f"Requesting music generation from {generate_url}")
                response = await client.post(
                    generate_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                result = response.json()

                if not result:
                    raise Exception("No response from Suno API")

                # Get audio IDs from response
                audio_ids = []
                if isinstance(result, list):
                    audio_ids = [item.get("id") for item in result if item.get("id")]
                elif isinstance(result, dict) and "id" in result:
                    audio_ids = [result["id"]]

                if not audio_ids:
                    raise Exception(f"No audio IDs in response: {result}")

                logger.info(f"Audio generation started. IDs: {audio_ids}")

                # Step 2: Poll for completion
                audio_url = None
                max_attempts = 60  # 5 minutes max
                for attempt in range(max_attempts):
                    time.sleep(5)  # Wait 5 seconds between polls

                    get_url = f"{self.base_url}/api/get?ids={','.join(audio_ids)}"
                    logger.info(f"Polling audio status (attempt {attempt + 1}/{max_attempts})...")

                    status_response = await client.get(get_url)
                    status_response.raise_for_status()
                    status_data = status_response.json()

                    if isinstance(status_data, list) and len(status_data) > 0:
                        audio_item = status_data[0]
                        status = audio_item.get("status")
                        audio_url = audio_item.get("audio_url")

                        logger.info(f"Status: {status}, URL: {audio_url}")

                        if status == "streaming" and audio_url:
                            logger.info("Music generation complete!")
                            break
                        elif status == "error":
                            error_msg = audio_item.get("error_message", "Unknown error")
                            raise Exception(f"Suno generation failed: {error_msg}")

                    if attempt == max_attempts - 1:
                        raise Exception("Timeout waiting for music generation")

                if not audio_url:
                    raise Exception("No audio URL received from Suno")

                # Step 3: Download the audio file
                logger.info(f"Downloading music from {audio_url}")
                audio_response = await client.get(audio_url)
                audio_response.raise_for_status()

                # Save to file
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)

                with open(output_path, "wb") as f:
                    f.write(audio_response.content)

                logger.info(f"Music saved to {output_path}")

                return {
                    "success": True,
                    "path": output_path,
                    "audio_url": audio_url,
                    "duration": duration
                }

        except Exception as e:
            logger.error(f"Error generating Suno music: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
suno_service = SunoMusicService()

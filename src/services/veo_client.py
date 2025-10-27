"""
Google Veo 3 video generation client service.
Handles AI video generation using Google's Veo 3 via Gemini API.
"""

from typing import Optional, Dict, Any, List
import logging
import asyncio
import time
import os
from pathlib import Path
from google import genai
from ..config import settings

logger = logging.getLogger(__name__)


class Veo3Service:
    """Service for generating cinematic videos using Google Veo 3."""

    def __init__(self):
        """Initialize Google Veo 3 client."""
        # Set API key as environment variable for the SDK
        os.environ['GEMINI_API_KEY'] = settings.google_api_key
        self.client = genai.Client()

    async def generate_video_clip(
        self,
        prompt: str,
        duration: int = 8,
        output_path: Optional[str] = None,
        aspect_ratio: str = "9:16",
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Generate a single video clip using Google Veo 3.

        Args:
            prompt: Detailed cinematic prompt for the video
            duration: Video duration in seconds (4, 6, or 8)
            output_path: Optional local path to save the video
            aspect_ratio: Video aspect ratio ("9:16" or "16:9")
            max_retries: Maximum number of retries for transient failures

        Returns:
            Dict with success status, video_data, and output_path
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    wait_time = 2 ** attempt * 30  # 30s, 60s, 120s
                    logger.info(f"Retry attempt {attempt + 1}/{max_retries} after {wait_time}s wait...")
                    await asyncio.sleep(wait_time)

                logger.info(f"Generating {duration}s video clip with Veo 3...")
                logger.info(f"Prompt: {prompt[:150]}...")

                # Start video generation operation
                # Note: Pass aspect_ratio in prompt for now as API config support is limited
                # Add aspect ratio instruction to prompt
                enhanced_prompt = f"{prompt}\n\nIMPORTANT: Generate in {aspect_ratio} aspect ratio (vertical portrait format)." if aspect_ratio == "9:16" else prompt

                operation = self.client.models.generate_videos(
                    model="veo-3.0-generate-preview",
                    prompt=enhanced_prompt
                )

                logger.info(f"Video generation operation started: {operation.name}")

                # Poll for completion (runs in executor to not block)
                def poll_operation():
                    while not operation.done:
                        logger.info("Waiting for video generation...")
                        time.sleep(10)
                        # Refresh operation status
                        refreshed_op = self.client.operations.get(operation)
                        if refreshed_op.done:
                            return refreshed_op
                    return operation

                # Run polling in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                completed_operation = await loop.run_in_executor(None, poll_operation)

                logger.info("Video generation completed!")

                # Log operation details for debugging
                logger.info(f"Operation done: {completed_operation.done}")
                logger.info(f"Operation response: {completed_operation.response}")
                if completed_operation.error:
                    error_msg = completed_operation.error
                    logger.error(f"Operation error: {error_msg}")

                    # Check if it's a retryable error (code 13 = INTERNAL)
                    if hasattr(error_msg, 'code') and error_msg.code == 13 and attempt < max_retries - 1:
                        logger.warning(f"Retryable error detected (code 13), will retry...")
                        last_error = error_msg
                        continue
                    elif hasattr(error_msg, 'get') and error_msg.get('code') == 13 and attempt < max_retries - 1:
                        logger.warning(f"Retryable error detected (code 13), will retry...")
                        last_error = error_msg
                        continue
                    else:
                        raise Exception(f"Video generation failed: {error_msg}")

                # Get the generated video from response
                if completed_operation.response and completed_operation.response.generated_videos:
                    generated_video = completed_operation.response.generated_videos[0]
                    video_uri = generated_video.video.uri

                    logger.info(f"Video URI: {video_uri}")

                    if output_path:
                        # Extract file name/ID from URI
                        # URI format: https://generativelanguage.googleapis.com/v1beta/files/FILE_ID:download?alt=media
                        file_name = video_uri.split('/files/')[1].split(':')[0]
                        logger.info(f"Downloading file: {file_name}")

                        # Download using SDK's file download method
                        def download_file():
                            video_file = self.client.files.get(name=file_name)
                            video_data = self.client.files.download(file=video_file)
                            return video_data

                        # Run in executor to not block
                        loop = asyncio.get_event_loop()
                        video_data = await loop.run_in_executor(None, download_file)

                        logger.info(f"Downloaded video: {len(video_data)} bytes")

                        # Save to output path
                        with open(output_path, 'wb') as f:
                            f.write(video_data)

                        logger.info(f"Saved generated video to {output_path}")

                        return {
                            "success": True,
                            "video_data": video_data,
                            "output_path": output_path,
                            "duration": duration
                        }
                    else:
                        # Just return the URI
                        return {
                            "success": True,
                            "video_uri": video_uri,
                            "duration": duration
                        }
                else:
                    # No video in response - might be retryable
                    if attempt < max_retries - 1:
                        logger.warning(f"No video in response, will retry...")
                        last_error = "No video in operation response"
                        continue
                    else:
                        raise Exception("No video in operation response")

            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Error on attempt {attempt + 1}: {e}")
                    last_error = e
                    continue
                else:
                    logger.error(f"Error generating video after {max_retries} attempts: {e}", exc_info=True)
                    return {
                        "success": False,
                        "error": str(e),
                        "message": f"Video generation failed after {max_retries} attempts: {str(e)}"
                    }

        # If we get here, all retries failed
        logger.error(f"All {max_retries} retry attempts failed. Last error: {last_error}")
        return {
            "success": False,
            "error": str(last_error),
            "message": f"Video generation failed after {max_retries} attempts"
        }

    async def generate_multi_clip_video(
        self,
        clip_prompts: List[str],
        output_dir: str = "/tmp"
    ) -> Dict[str, Any]:
        """
        Generate multiple video clips in parallel.

        Args:
            clip_prompts: List of prompts for each clip
            output_dir: Directory to save clips

        Returns:
            Dict with list of clip paths and success status
        """
        try:
            logger.info(f"Generating {len(clip_prompts)} video clips in parallel...")

            tasks = []
            for i, prompt in enumerate(clip_prompts):
                output_path = f"{output_dir}/clip_{i+1}.mp4"
                task = self.generate_video_clip(
                    prompt=prompt,
                    duration=settings.clip_duration,
                    output_path=output_path
                )
                tasks.append(task)

            # Generate all clips in parallel
            results = await asyncio.gather(*tasks)

            # Check if all succeeded
            clip_paths = []
            for i, result in enumerate(results):
                if result.get("success"):
                    clip_paths.append(result["output_path"])
                else:
                    logger.error(f"Clip {i+1} failed: {result.get('error')}")
                    return {
                        "success": False,
                        "error": f"Clip {i+1} generation failed",
                        "message": result.get("message")
                    }

            logger.info(f"Successfully generated {len(clip_paths)} video clips")
            return {
                "success": True,
                "clip_paths": clip_paths,
                "num_clips": len(clip_paths)
            }

        except Exception as e:
            logger.error(f"Error in multi-clip generation: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Multi-clip generation failed: {str(e)}"
            }


# Global instance
veo3_service = Veo3Service()

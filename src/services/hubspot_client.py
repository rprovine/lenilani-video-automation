"""
HubSpot integration service for video uploads and social media publishing.
Handles uploading videos to HubSpot file manager and publishing to YouTube via HubSpot Social.
"""

from typing import Optional, Dict, Any
import logging
import httpx
from pathlib import Path
import asyncio
import json
from ..config import settings

logger = logging.getLogger(__name__)


class HubSpotService:
    """Service for HubSpot video uploads and YouTube publishing."""

    def __init__(self):
        """Initialize HubSpot client."""
        self.access_token = settings.hubspot_access_token
        self.portal_id = settings.hubspot_portal_id
        self.base_url = "https://api.hubapi.com"

        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    async def upload_video_to_file_manager(
        self,
        video_path: str,
        video_name: str,
        folder_path: Optional[str] = "/AI Generated Videos"
    ) -> Dict[str, Any]:
        """
        Upload a video to HubSpot's file manager.

        Args:
            video_path: Local path to the video file
            video_name: Name for the video in HubSpot
            folder_path: Optional folder path in HubSpot file manager

        Returns:
            Dict with success status, file ID, and file URL
        """
        try:
            logger.info(f"Uploading video to HubSpot: {video_name}")

            if not Path(video_path).exists():
                raise FileNotFoundError(f"Video not found: {video_path}")

            # Read video file
            with open(video_path, 'rb') as f:
                video_data = f.read()

            # HubSpot file upload endpoint
            upload_url = f"{self.base_url}/filemanager/api/v3/files/upload"

            # Prepare multipart form data
            files = {
                'file': (video_name, video_data, 'video/mp4')
            }

            data = {
                'options': {
                    'access': 'PUBLIC_INDEXABLE',
                    'ttl': 'P3M',  # 3 months TTL
                    'overwrite': False,
                    'duplicateValidationStrategy': 'NONE'
                }
            }

            if folder_path:
                data['options']['folderPath'] = folder_path

            # Upload using httpx
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    upload_url,
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    files=files,
                    data={'options': json.dumps(data['options'])}
                )

                if response.status_code not in [200, 201]:
                    error_detail = response.text
                    logger.error(f"HubSpot upload failed: {response.status_code} - {error_detail}")
                    raise Exception(f"HubSpot upload failed: {error_detail}")

                result = response.json()
                logger.info(f"Video uploaded successfully to HubSpot")
                logger.info(f"File ID: {result.get('id')}")
                logger.info(f"File URL: {result.get('url')}")

                return {
                    "success": True,
                    "file_id": result.get('id'),
                    "file_url": result.get('url'),
                    "file_name": video_name,
                    "message": "Video uploaded to HubSpot successfully"
                }

        except Exception as e:
            logger.error(f"Error uploading video to HubSpot: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"HubSpot upload failed: {str(e)}"
            }

    async def create_social_post_to_youtube(
        self,
        video_url: str,
        title: str,
        description: str,
        channel_guid: str,
        tags: Optional[list] = None,
        publish_immediately: bool = False
    ) -> Dict[str, Any]:
        """
        Create a social media post in HubSpot that publishes to YouTube.
        Requires YouTube account to be connected in HubSpot Social settings.

        Args:
            video_url: Public URL of the video file
            title: YouTube video title
            description: YouTube video description
            channel_guid: YouTube channel GUID from HubSpot
            tags: Optional list of tags/hashtags
            publish_immediately: Whether to publish immediately or schedule

        Returns:
            Dict with success status and broadcast ID
        """
        try:
            logger.info(f"Creating YouTube social post in HubSpot: {title}")

            # HubSpot Social publishing endpoint
            social_url = f"{self.base_url}/social/v1/broadcasts"

            # Construct post content
            # For immediate publishing, set triggerAt to current time (not None, not future)
            import time
            current_time_ms = int(time.time() * 1000)

            post_data = {
                "channelGuid": channel_guid,
                "broadcastGuid": None,  # Let HubSpot generate
                "status": "SCHEDULED",  # Use SCHEDULED status with triggerAt for immediate publish
                "triggerAt": current_time_ms if publish_immediately else current_time_ms + 300000,  # Now or 5 min from now
                "content": description,
                "videoUrl": video_url,
                "title": title
            }

            if tags:
                post_data["tags"] = tags

            # Create social broadcast
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    social_url,
                    headers=self.headers,
                    json=post_data
                )

                if response.status_code not in [200, 201]:
                    error_detail = response.text
                    logger.error(f"HubSpot social post creation failed: {response.status_code} - {error_detail}")
                    raise Exception(f"Social post creation failed: {error_detail}")

                result = response.json()
                logger.info(f"Social post created successfully in HubSpot")
                logger.info(f"Broadcast ID: {result.get('broadcastGuid')}")

                return {
                    "success": True,
                    "broadcast_id": result.get('broadcastGuid'),
                    "status": result.get('status'),
                    "platform": "youtube",
                    "message": "YouTube post created via HubSpot successfully"
                }

        except Exception as e:
            logger.error(f"Error creating YouTube social post: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"YouTube post creation failed: {str(e)}"
            }

    async def get_connected_youtube_channel(self) -> Dict[str, Any]:
        """
        Get the connected YouTube channel details from HubSpot.

        Returns:
            Dict with channel information
        """
        try:
            logger.info("Fetching connected YouTube channel from HubSpot...")

            # Get all connected channels
            channels_url = f"{self.base_url}/social/v1/channels"

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    channels_url,
                    headers=self.headers
                )

                if response.status_code != 200:
                    error_detail = response.text
                    logger.error(f"Failed to fetch channels: {response.status_code} - {error_detail}")
                    raise Exception(f"Failed to fetch channels: {error_detail}")

                channels = response.json()

                # Find YouTube channel
                youtube_channel = None
                for channel in channels.get('objects', []):
                    if channel.get('channelType') == 'YOUTUBE':
                        youtube_channel = channel
                        break

                if not youtube_channel:
                    logger.warning("No YouTube channel connected to HubSpot")
                    return {
                        "success": False,
                        "message": "No YouTube channel connected to HubSpot"
                    }

                logger.info(f"Found YouTube channel: {youtube_channel.get('name')}")

                return {
                    "success": True,
                    "channel_guid": youtube_channel.get('channelGuid'),
                    "channel_name": youtube_channel.get('name'),
                    "channel_id": youtube_channel.get('channelId'),
                    "message": "YouTube channel found"
                }

        except Exception as e:
            logger.error(f"Error fetching YouTube channel: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to fetch YouTube channel: {str(e)}"
            }

    async def upload_and_publish_to_youtube(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: Optional[list] = None,
        publish_immediately: bool = False
    ) -> Dict[str, Any]:
        """
        Complete workflow: Upload video to HubSpot and publish to YouTube.

        Args:
            video_path: Local path to the video file
            title: YouTube video title
            description: YouTube video description
            tags: Optional list of tags
            publish_immediately: Whether to publish immediately

        Returns:
            Dict with complete workflow results
        """
        try:
            logger.info(f"Starting complete YouTube publishing workflow for: {title}")

            # Step 1: Upload video to HubSpot file manager
            video_name = Path(video_path).name
            upload_result = await self.upload_video_to_file_manager(
                video_path=video_path,
                video_name=video_name,
                folder_path="/AI Generated Videos"
            )

            if not upload_result.get("success"):
                return upload_result

            video_url = upload_result.get("file_url")
            logger.info(f"Video uploaded, URL: {video_url}")

            # Step 2: Get YouTube channel GUID
            channel_result = await self.get_connected_youtube_channel()
            if not channel_result.get("success"):
                return channel_result

            channel_guid = channel_result.get("channel_guid")
            logger.info(f"Using YouTube channel: {channel_result.get('channel_name')}")

            # Step 3: Create social post to YouTube
            post_result = await self.create_social_post_to_youtube(
                video_url=video_url,
                title=title,
                description=description,
                channel_guid=channel_guid,
                tags=tags,
                publish_immediately=publish_immediately
            )

            if not post_result.get("success"):
                return {
                    **post_result,
                    "file_url": video_url,  # Include file URL even if post failed
                    "message": f"Video uploaded but YouTube post failed: {post_result.get('message')}"
                }

            logger.info("✅ Complete workflow successful!")

            return {
                "success": True,
                "file_url": video_url,
                "file_id": upload_result.get("file_id"),
                "broadcast_id": post_result.get("broadcast_id"),
                "youtube_channel": channel_result.get("channel_name"),
                "status": post_result.get("status"),
                "message": "Video uploaded and published to YouTube via HubSpot successfully"
            }

        except Exception as e:
            logger.error(f"Error in YouTube publishing workflow: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"YouTube publishing workflow failed: {str(e)}"
            }


# Global instance
hubspot_service = HubSpotService()

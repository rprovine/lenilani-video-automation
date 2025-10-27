"""
Google Drive upload service.
Uploads generated videos to a specific Google Drive folder.
"""

from typing import Optional, Dict, Any
import logging
from pathlib import Path
import subprocess

logger = logging.getLogger(__name__)


class GoogleDriveUploader:
    """Service for uploading videos to Google Drive."""

    def __init__(self):
        """Initialize Google Drive uploader."""
        # Google Drive folder: "AI Generated Videos"
        # Account: rprovine@kointyme.com
        self.folder_name = "AI Generated Videos"
        self.account_email = "rprovine@kointyme.com"

    async def upload_video(
        self,
        video_path: str,
        title: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a video to Google Drive using local Google Drive sync.

        Args:
            video_path: Path to the video file
            title: Video title (will be filename)
            description: Optional description

        Returns:
            Dict with success status and file path
        """
        try:
            logger.info(f"Uploading video to Google Drive: {title}")

            if not Path(video_path).exists():
                raise FileNotFoundError(f"Video not found: {video_path}")

            # Check if Google Drive is synced locally
            google_drive_paths = [
                Path("/Users/renoprovine/Library/CloudStorage/GoogleDrive-rprovine@kointyme.com/My Drive"),
                Path.home() / "Library" / "CloudStorage" / "GoogleDrive-rprovine@kointyme.com" / "My Drive",
                Path.home() / "Google Drive",
                Path.home() / "GoogleDrive",
                "/Users/renoprovine/Google Drive",
                "/Volumes/GoogleDrive"
            ]

            drive_path = None
            for path in google_drive_paths:
                if path.exists():
                    drive_path = path
                    logger.info(f"Found Google Drive at: {drive_path}")
                    break

            if not drive_path:
                logger.warning("Google Drive folder not found locally - saving to /tmp")
                # Fallback: just copy to a local folder
                import shutil
                output_dir = Path("/tmp/ai_generated_videos")
                output_dir.mkdir(exist_ok=True)

                # Create a sanitized filename
                safe_filename = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                output_path = output_dir / f"{safe_filename}.mp4"

                shutil.copy(video_path, output_path)

                return {
                    "success": True,
                    "platform": "google_drive",
                    "path": str(output_path),
                    "message": f"Video saved locally (Google Drive not found): {output_path}"
                }

            # Find the "AI Generated Videos" folder
            # Check if "My Drive" subfolder exists (common for Google Drive Desktop app)
            # Skip this check if we're already at the My Drive level
            if not str(drive_path).endswith("My Drive"):
                my_drive = drive_path / "My Drive"
                if my_drive.exists():
                    drive_path = my_drive
                    logger.info(f"Using My Drive subfolder: {drive_path}")

            target_folder = drive_path / self.folder_name
            if not target_folder.exists():
                logger.info(f"Creating folder: {target_folder}")
                target_folder.mkdir(parents=True, exist_ok=True)

            # Create a sanitized filename
            safe_filename = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
            output_path = target_folder / f"{safe_filename}.mp4"

            # Copy video to Google Drive folder
            import shutil
            shutil.copy(video_path, output_path)

            logger.info(f"Video uploaded to Google Drive: {output_path}")

            # Write description to a text file if provided
            if description:
                desc_path = target_folder / f"{safe_filename}_description.txt"
                with open(desc_path, 'w') as f:
                    f.write(description)

            return {
                "success": True,
                "platform": "google_drive",
                "path": str(output_path),
                "url": f"Google Drive: {self.folder_name}/{safe_filename}.mp4",
                "message": f"Video uploaded to Google Drive successfully"
            }

        except Exception as e:
            logger.error(f"Error uploading to Google Drive: {e}", exc_info=True)
            return {
                "success": False,
                "platform": "google_drive",
                "error": str(e),
                "message": f"Google Drive upload failed: {str(e)}"
            }


# Global instance
google_drive_uploader = GoogleDriveUploader()

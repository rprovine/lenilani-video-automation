"""
Music Library Service
Randomly selects music from Google Drive library and extracts 30-second segments.
"""

import random
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class MusicLibraryService:
    """Service for managing and selecting music from the library."""

    def __init__(self, library_path: str):
        """
        Initialize music library service.

        Args:
            library_path: Path to the music library folder
        """
        self.library_path = Path(library_path)
        if not self.library_path.exists():
            raise ValueError(f"Music library path does not exist: {library_path}")

    def get_all_music_files(self) -> List[Path]:
        """
        Get all music files from the library.

        Returns:
            List of Path objects for music files
        """
        # Support both WAV and MP3 files
        music_files = []
        for extension in ['*.wav', '*.mp3', '*.WAV', '*.MP3']:
            music_files.extend(self.library_path.glob(extension))

        # Include all files (don't filter out " (1)" - they're different versions)
        logger.info(f"Found {len(music_files)} music files in library")
        return music_files

    def get_audio_duration(self, audio_path: Path) -> float:
        """
        Get duration of audio file in seconds using ffprobe.

        Args:
            audio_path: Path to audio file

        Returns:
            Duration in seconds
        """
        try:
            result = subprocess.run(
                [
                    'ffprobe', '-v', 'error',
                    '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1',
                    str(audio_path)
                ],
                capture_output=True,
                text=True,
                check=True
            )
            duration = float(result.stdout.strip())
            return duration
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return 0.0

    def select_random_segment(
        self,
        output_path: str = "/tmp/music_segment.mp3",
        segment_duration: int = 30
    ) -> Dict[str, Any]:
        """
        Randomly select a music file and extract a random 30-second segment.

        Args:
            output_path: Where to save the extracted segment
            segment_duration: Length of segment in seconds (default 30)

        Returns:
            Dict with success status, file path, and metadata
        """
        try:
            # Get all available music files
            music_files = self.get_all_music_files()

            if not music_files:
                raise ValueError("No music files found in library")

            # Randomly select a file
            selected_file = random.choice(music_files)
            logger.info(f"Randomly selected: {selected_file.name}")

            # Get duration of selected file
            duration = self.get_audio_duration(selected_file)
            if duration == 0:
                raise ValueError(f"Could not determine duration of {selected_file.name}")

            logger.info(f"File duration: {duration:.2f} seconds")

            # Calculate random start time
            # Ensure we don't go past the end
            max_start = max(0, duration - segment_duration)
            start_time = random.uniform(0, max_start)

            logger.info(f"Extracting {segment_duration}s segment starting at {start_time:.2f}s")

            # Extract segment using ffmpeg
            subprocess.run(
                [
                    'ffmpeg',
                    '-i', str(selected_file),
                    '-ss', str(start_time),
                    '-t', str(segment_duration),
                    '-c:a', 'libmp3lame',  # Convert to MP3
                    '-b:a', '192k',  # High quality audio
                    '-y',
                    output_path
                ],
                capture_output=True,
                check=True
            )

            logger.info(f"Music segment saved to {output_path}")

            return {
                "success": True,
                "path": output_path,
                "source_file": selected_file.name,
                "start_time": start_time,
                "duration": segment_duration,
                "source_duration": duration
            }

        except Exception as e:
            logger.error(f"Error selecting music segment: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
music_library = MusicLibraryService(
    library_path="/Users/renoprovine/Library/CloudStorage/GoogleDrive-rprovine@kointyme.com/My Drive/AI Generated Videos/Music Library"
)

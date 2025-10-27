"""
Video composition utility using FFmpeg.
Handles merging video clips, adding title cards, and creating the final video.
"""

import subprocess
import logging
from typing import List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class VideoComposer:
    """Utility for composing final videos from clips and images."""

    @staticmethod
    async def merge_clips(
        clip_paths: List[str],
        output_path: str,
        include_transitions: bool = True
    ) -> dict:
        """
        Merge multiple video clips into a single video.

        Args:
            clip_paths: List of paths to video clips (in order)
            output_path: Path for the output video
            include_transitions: Whether to add smooth transitions between clips

        Returns:
            Dict with success status and output path
        """
        try:
            logger.info(f"Merging {len(clip_paths)} video clips...")

            # Verify all clips exist
            for clip_path in clip_paths:
                if not Path(clip_path).exists():
                    raise FileNotFoundError(f"Clip not found: {clip_path}")

            # Create a concat file for FFmpeg
            concat_file = "/tmp/concat_list.txt"
            with open(concat_file, "w") as f:
                for clip_path in clip_paths:
                    f.write(f"file '{clip_path}'\n")

            # FFmpeg command to concatenate videos
            if include_transitions:
                # With crossfade transitions (more complex)
                # For now, use simple concatenation - transitions can be added later
                cmd = [
                    "ffmpeg",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", concat_file,
                    "-c", "copy",
                    "-y",  # Overwrite output file if exists
                    output_path
                ]
            else:
                # Simple concatenation
                cmd = [
                    "ffmpeg",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", concat_file,
                    "-c", "copy",
                    "-y",
                    output_path
                ]

            # Run FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return {
                    "success": False,
                    "error": f"FFmpeg failed: {result.stderr}",
                    "message": "Video merge failed"
                }

            logger.info(f"Successfully merged {len(clip_paths)} clips into {output_path}")
            return {
                "success": True,
                "output_path": output_path,
                "num_clips": len(clip_paths)
            }

        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Clip file not found"
            }
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg timeout - video merge took too long")
            return {
                "success": False,
                "error": "Operation timeout",
                "message": "Video merge timed out"
            }
        except Exception as e:
            logger.error(f"Error merging clips: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Video merge failed: {str(e)}"
            }

    @staticmethod
    async def image_to_video(
        image_path: str,
        output_path: str,
        duration: float = 3.0,
        width: int = 1080,
        height: int = 1920
    ) -> dict:
        """
        Convert a static image to a video clip (for title cards).

        Args:
            image_path: Path to the image
            output_path: Path for the output video
            duration: Duration of the video in seconds
            width: Video width (default 1080 for 9:16)
            height: Video height (default 1920 for 9:16)

        Returns:
            Dict with success status and output path
        """
        try:
            logger.info(f"Converting image to {duration}s video clip...")

            if not Path(image_path).exists():
                raise FileNotFoundError(f"Image not found: {image_path}")

            # FFmpeg command to create video from image
            cmd = [
                "ffmpeg",
                "-loop", "1",  # Loop the image
                "-i", image_path,
                "-c:v", "libx264",  # H.264 codec
                "-t", str(duration),  # Duration
                "-pix_fmt", "yuv420p",
                "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
                "-r", "30",  # 30 fps
                "-y",
                output_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return {
                    "success": False,
                    "error": f"FFmpeg failed: {result.stderr}",
                    "message": "Image to video conversion failed"
                }

            logger.info(f"Successfully converted image to video: {output_path}")
            return {
                "success": True,
                "output_path": output_path,
                "duration": duration
            }

        except FileNotFoundError as e:
            logger.error(f"Image file not found: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Image file not found"
            }
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg timeout - image conversion took too long")
            return {
                "success": False,
                "error": "Operation timeout",
                "message": "Image conversion timed out"
            }
        except Exception as e:
            logger.error(f"Error converting image to video: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Image conversion failed: {str(e)}"
            }

    @staticmethod
    async def add_text_overlay(
        video_path: str,
        output_path: str,
        text: str,
        position: str = "center",
        fontsize: int = 48,
        fontcolor: str = "white"
    ) -> dict:
        """
        Add text overlay to a video (for title cards, captions, etc.).

        Args:
            video_path: Path to the input video
            output_path: Path for the output video
            text: Text to overlay
            position: Position (center, top, bottom)
            fontsize: Font size
            fontcolor: Font color

        Returns:
            Dict with success status and output path
        """
        try:
            logger.info(f"Adding text overlay to video...")

            if not Path(video_path).exists():
                raise FileNotFoundError(f"Video not found: {video_path}")

            # Position coordinates
            positions = {
                "center": "x=(w-text_w)/2:y=(h-text_h)/2",
                "top": "x=(w-text_w)/2:y=100",
                "bottom": "x=(w-text_w)/2:y=h-text_h-100"
            }
            pos = positions.get(position, positions["center"])

            # FFmpeg command with text overlay
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vf", f"drawtext=text='{text}':fontsize={fontsize}:fontcolor={fontcolor}:{pos}:box=1:boxcolor=black@0.5:boxborderw=5",
                "-codec:a", "copy",
                "-y",
                output_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return {
                    "success": False,
                    "error": f"FFmpeg failed: {result.stderr}",
                    "message": "Text overlay failed"
                }

            logger.info(f"Successfully added text overlay: {output_path}")
            return {
                "success": True,
                "output_path": output_path
            }

        except FileNotFoundError as e:
            logger.error(f"Video file not found: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Video file not found"
            }
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg timeout - text overlay took too long")
            return {
                "success": False,
                "error": "Operation timeout",
                "message": "Text overlay timed out"
            }
        except Exception as e:
            logger.error(f"Error adding text overlay: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Text overlay failed: {str(e)}"
            }

    @staticmethod
    def _check_has_audio(video_path: str) -> bool:
        """Check if a video file has an audio stream."""
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "a:0",
                "-show_entries", "stream=codec_type",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0 and result.stdout.strip() == "audio"
        except Exception as e:
            logger.warning(f"Could not check audio stream: {e}")
            return False

    @staticmethod
    async def add_audio_to_video(
        video_path: str,
        audio_path: str,
        output_path: str,
        audio_volume: float = 1.0,
        video_volume: float = 0.3,  # Lower original video audio to 30%
        music_path: Optional[str] = None,
        music_volume: float = 0.25,  # Background music at 25%
        enable_ducking: bool = True  # Enable professional audio ducking
    ) -> dict:
        """
        Add voiceover and optional background music to a video with professional audio ducking.

        Audio ducking automatically lowers background music and video audio when voiceover is speaking,
        creating a polished, professional sound like high-end video production.

        Args:
            video_path: Path to the input video
            audio_path: Path to the voiceover audio file
            output_path: Path for the output video
            audio_volume: Volume level for voiceover (0.0 to 1.0+)
            video_volume: Volume level for original video audio (0.0 to 1.0)
            music_path: Optional path to background music file
            music_volume: Volume level for background music (0.0 to 1.0)
            enable_ducking: Enable audio ducking (recommended for professional quality)

        Returns:
            Dict with success status and output path
        """
        try:
            # Check if video has audio
            video_has_audio = VideoComposer._check_has_audio(video_path)

            if not video_has_audio:
                logger.info("Video has no audio stream (video-only), skipping video audio in mix")

            if music_path and Path(music_path).exists():
                if video_has_audio:
                    logger.info(f"Professional audio mixing: video + voiceover + music with ducking")
                    logger.info(f"Base Volumes - Video: {video_volume}, Voiceover: {audio_volume}, Music: {music_volume}")
                else:
                    logger.info(f"Professional audio mixing: voiceover + music with ducking (no video audio)")
                    logger.info(f"Base Volumes - Voiceover: {audio_volume}, Music: {music_volume}")
            else:
                if video_has_audio:
                    logger.info(f"Professional audio mixing: video + voiceover with ducking")
                    logger.info(f"Base Volumes - Video: {video_volume}, Voiceover: {audio_volume}")
                else:
                    logger.info(f"Adding voiceover only (no video audio or music)")
                    logger.info(f"Base Volume - Voiceover: {audio_volume}")

            if not Path(video_path).exists():
                raise FileNotFoundError(f"Video not found: {video_path}")
            if not Path(audio_path).exists():
                raise FileNotFoundError(f"Audio not found: {audio_path}")

            # Build professional FFmpeg command with audio ducking
            if music_path and Path(music_path).exists() and enable_ducking:
                if video_has_audio:
                    # PROFESSIONAL 3-WAY MIX WITH DUCKING (video audio + voiceover + music)
                    # Use asplit to create three copies of voiceover for multiple sidechains and mix
                    filter_complex = (
                        # Prepare voiceover and split for triple use (2 sidechains + mix)
                        f"[1:a]volume={audio_volume}[vo_raw];"
                        "[vo_raw]asplit=3[vo1][vo2][vo3];"

                        # Prepare music with fade in/out
                        f"[2:a]afade=t=in:st=0:d=1,afade=t=out:st=27:d=3,volume={music_volume}[music_raw];"

                        # Duck music when voiceover speaks (using vo1 for sidechain)
                        "[vo1][music_raw]sidechaincompress=threshold=0.03:ratio=4:attack=20:release=250:level_sc=1[music_ducked];"

                        # Prepare video audio
                        f"[0:a]volume={video_volume}[video_raw];"

                        # Duck video audio when voiceover speaks (using vo2 for sidechain)
                        "[vo2][video_raw]sidechaincompress=threshold=0.04:ratio=3:attack=20:release=250:level_sc=1[video_ducked];"

                        # Mix all three audio streams (using vo3 for mix)
                        "[vo3][music_ducked][video_ducked]amix=inputs=3:duration=first:dropout_transition=2:normalize=0[mixed];"

                        # Final polish with loudnorm, compression, and limiting
                        "[mixed]loudnorm=I=-16:TP=-1.5:LRA=11,acompressor=threshold=-20dB:ratio=3:attack=5:release=50:makeup=2dB,alimiter=limit=0.95:attack=5:release=50[out]"
                    )
                else:
                    # PROFESSIONAL 2-WAY MIX WITH DUCKING (voiceover + music only, no video audio)
                    # Use asplit to create two copies of voiceover for sidechain and mix
                    filter_complex = (
                        # Prepare voiceover with volume and split for dual use
                        f"[1:a]volume={audio_volume}[vo_raw];"
                        "[vo_raw]asplit=2[vo1][vo2];"

                        # Prepare music with fade in/out
                        f"[2:a]afade=t=in:st=0:d=1,afade=t=out:st=17:d=3,volume={music_volume}[music_raw];"

                        # Duck music when voiceover speaks (using vo1 for sidechain)
                        "[vo1][music_raw]sidechaincompress=threshold=0.03:ratio=4:attack=20:release=250:level_sc=1[music_ducked];"

                        # Mix voiceover and ducked music (using vo2 for mix)
                        "[vo2][music_ducked]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[mixed];"

                        # Final polish with loudnorm, compression, and limiting
                        "[mixed]loudnorm=I=-16:TP=-1.5:LRA=11,acompressor=threshold=-20dB:ratio=3:attack=5:release=50:makeup=2dB,alimiter=limit=0.95:attack=5:release=50[out]"
                    )

                cmd = [
                    "ffmpeg",
                    "-i", video_path,
                    "-i", audio_path,
                    "-i", music_path,
                    "-filter_complex", filter_complex,
                    "-map", "0:v",      # Video from first input
                    "-map", "[out]",    # Audio from filter
                    "-c:v", "copy",     # Copy video without re-encoding
                    "-c:a", "aac",      # High-quality AAC audio
                    "-b:a", "256k",     # Higher bitrate for professional quality
                    "-ar", "48000",     # 48kHz sample rate (broadcast standard)
                    "-y",
                    output_path
                ]
            elif music_path and Path(music_path).exists():
                # 3-way or 2-way mix without ducking (fallback)
                if video_has_audio:
                    filter_complex = (
                        f"[0:a]volume={video_volume}[a1];"
                        f"[1:a]volume={audio_volume},loudnorm=I=-16:TP=-1.5:LRA=11[a2];"
                        f"[2:a]afade=t=in:st=0:d=1,afade=t=out:st=27:d=3,volume={music_volume}[a3];"
                        "[a1][a2][a3]amix=inputs=3:duration=first:dropout_transition=2,alimiter=limit=0.95[out]"
                    )
                else:
                    # 2-way mix without ducking (voiceover + music, no video audio)
                    filter_complex = (
                        f"[1:a]volume={audio_volume},loudnorm=I=-16:TP=-1.5:LRA=11[a1];"
                        f"[2:a]afade=t=in:st=0:d=1,afade=t=out:st=17:d=3,volume={music_volume}[a2];"
                        "[a1][a2]amix=inputs=2:duration=first:dropout_transition=2,alimiter=limit=0.95[out]"
                    )

                cmd = [
                    "ffmpeg",
                    "-i", video_path,
                    "-i", audio_path,
                    "-i", music_path,
                    "-filter_complex", filter_complex,
                    "-map", "0:v",
                    "-map", "[out]",
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", "256k",
                    "-ar", "48000",
                    "-shortest",
                    "-y",
                    output_path
                ]
            elif enable_ducking and video_has_audio:
                # 2-way mix with ducking (video audio ducked by voiceover)
                # Use asplit to create two copies of voiceover for sidechain and mix
                filter_complex = (
                    f"[1:a]volume={audio_volume}[vo_raw];"
                    "[vo_raw]asplit=2[vo1][vo2];"
                    f"[0:a]volume={video_volume}[video_raw];"
                    "[vo1][video_raw]sidechaincompress=threshold=0.04:ratio=3:attack=20:release=250:level_sc=1[video_ducked];"
                    "[vo2][video_ducked]amix=inputs=2:duration=first:dropout_transition=2[mixed];"
                    "[mixed]loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.95[out]"
                )

                cmd = [
                    "ffmpeg",
                    "-i", video_path,
                    "-i", audio_path,
                    "-filter_complex", filter_complex,
                    "-map", "0:v",
                    "-map", "[out]",
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", "256k",
                    "-ar", "48000",
                    "-shortest",
                    "-y",
                    output_path
                ]
            else:
                # Simple 2-way mix without ducking or voiceover-only (fallback)
                if video_has_audio:
                    filter_complex = (
                        f"[0:a]volume={video_volume}[a1];"
                        f"[1:a]volume={audio_volume},loudnorm=I=-16:TP=-1.5:LRA=11[a2];"
                        "[a1][a2]amix=inputs=2:duration=first:dropout_transition=2,alimiter=limit=0.95[out]"
                    )

                    cmd = [
                        "ffmpeg",
                        "-i", video_path,
                        "-i", audio_path,
                        "-filter_complex", filter_complex,
                        "-map", "0:v",
                        "-map", "[out]",
                        "-c:v", "copy",
                        "-c:a", "aac",
                        "-b:a", "256k",
                        "-ar", "48000",
                        "-shortest",
                        "-y",
                        output_path
                    ]
                else:
                    # Voiceover-only (no video audio, no music)
                    filter_complex = f"[1:a]volume={audio_volume},loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.95[out]"

                    cmd = [
                        "ffmpeg",
                        "-i", video_path,
                        "-i", audio_path,
                        "-filter_complex", filter_complex,
                        "-map", "0:v",
                        "-map", "[out]",
                        "-c:v", "copy",
                        "-c:a", "aac",
                        "-b:a", "256k",
                        "-ar", "48000",
                        "-shortest",
                        "-y",
                        output_path
                    ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return {
                    "success": False,
                    "error": f"FFmpeg failed: {result.stderr}",
                    "message": "Audio mixing failed"
                }

            logger.info(f"Professional audio mix complete: {output_path}")
            return {
                "success": True,
                "output_path": output_path
            }

        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Input file not found"
            }
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg timeout - audio mixing took too long")
            return {
                "success": False,
                "error": "Operation timeout",
                "message": "Audio mixing timed out"
            }
        except Exception as e:
            logger.error(f"Error adding audio: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Audio mixing failed: {str(e)}"
            }

    @staticmethod
    async def compose_final_video(
        clip_paths: List[str],
        title_card_image_path: Optional[str],
        output_path: str,
        title_card_duration: float = 3.0,
        voiceover_audio_path: Optional[str] = None,
        music_audio_path: Optional[str] = None
    ) -> dict:
        """
        Compose the final video from clips and title card, optionally with voiceover and music.

        Args:
            clip_paths: List of video clip paths
            title_card_image_path: Optional path to title card image
            output_path: Path for final output video
            title_card_duration: Duration of title card in seconds
            voiceover_audio_path: Optional path to voiceover audio file
            music_audio_path: Optional path to background music file

        Returns:
            Dict with success status and output path
        """
        try:
            logger.info("Composing final video...")

            all_clips = []

            # If we have a title card, convert it to video first
            if title_card_image_path and Path(title_card_image_path).exists():
                logger.info("Converting title card to video...")
                title_card_video = "/tmp/title_card_video.mp4"
                title_result = await VideoComposer.image_to_video(
                    image_path=title_card_image_path,
                    output_path=title_card_video,
                    duration=title_card_duration
                )

                if title_result.get("success"):
                    all_clips.append(title_card_video)
                else:
                    logger.warning("Title card conversion failed, skipping...")

            # Add all video clips
            all_clips.extend(clip_paths)

            if len(all_clips) == 0:
                raise ValueError("No clips available for composition")

            # Determine output path (temp if we need to add audio)
            video_only_path = output_path if not voiceover_audio_path else "/tmp/video_no_audio.mp4"

            # If only one clip, just copy it
            if len(all_clips) == 1:
                logger.info("Only one clip, copying directly...")
                import shutil
                shutil.copy(all_clips[0], video_only_path)
                merge_result = {
                    "success": True,
                    "output_path": video_only_path,
                    "num_clips": 1
                }
            else:
                # Merge all clips
                logger.info(f"Merging {len(all_clips)} total segments...")
                merge_result = await VideoComposer.merge_clips(
                    clip_paths=all_clips,
                    output_path=video_only_path,
                    include_transitions=False  # Simple concat for now
                )

            if not merge_result.get("success"):
                return merge_result

            # If we have voiceover audio, mix it with the video (and optional music)
            if voiceover_audio_path and Path(voiceover_audio_path).exists():
                logger.info("Adding professional audio mix with ducking...")
                audio_result = await VideoComposer.add_audio_to_video(
                    video_path=video_only_path,
                    audio_path=voiceover_audio_path,
                    output_path=output_path,
                    audio_volume=1.0,    # Full voiceover volume
                    video_volume=0.3,    # Video audio at 30%
                    music_path=music_audio_path,
                    music_volume=0.4,    # Music at 40% for better audibility
                    enable_ducking=True  # Enable professional audio ducking
                )

                if audio_result.get("success"):
                    logger.info(f"Final video with voiceover composed successfully: {output_path}")
                    return audio_result
                else:
                    logger.warning("Voiceover mixing failed, using video without voiceover")
                    # Copy video-only version to final output
                    import shutil
                    shutil.copy(video_only_path, output_path)

            logger.info(f"Final video composed successfully: {output_path}")
            return {
                "success": True,
                "output_path": output_path,
                "num_clips": len(all_clips)
            }

        except Exception as e:
            logger.error(f"Error composing final video: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Final composition failed: {str(e)}"
            }


# Global instance
video_composer = VideoComposer()

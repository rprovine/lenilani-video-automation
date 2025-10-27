"""
Video generation workflow orchestrator.
Coordinates the entire process from topic research to video generation and social media publishing.
"""

from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
from ..services.claude_client import claude_service
from ..services.veo_client import veo3_service
from ..services.google_image_client import google_image_service
from ..services.google_drive_uploader import google_drive_uploader
from ..services.elevenlabs_client import elevenlabs_service
from ..services.hubspot_client import hubspot_service
from ..utils.video_composer import video_composer
from ..config import settings

logger = logging.getLogger(__name__)


# LeniLani Consulting services for topic alignment
LENILANI_SERVICES = [
    "AI Integration & Automation",
    "Website Development & Design",
    "Digital Marketing & SEO",
    "E-commerce Solutions",
    "Business Process Optimization",
    "Cloud Infrastructure & Migration",
    "Cybersecurity Consulting",
    "Data Analytics & Business Intelligence"
]


class VideoGenerator:
    """Main workflow for generating viral video content."""

    async def generate_and_publish(
        self,
        topic: Optional[str] = None,
        category: Optional[str] = None,
        publish_immediately: bool = True
    ) -> Dict[str, Any]:
        """
        Complete workflow: research → generate → compose → publish.

        Args:
            topic: Optional specific topic (if None, will research trending topics)
            category: Optional category focus (e.g., "AI", "automation")
            publish_immediately: Whether to publish to social media right away

        Returns:
            Dict with success status, video paths, URLs, and metadata
        """
        errors = []

        try:
            logger.info("=" * 80)
            logger.info("VIDEO GENERATION WORKFLOW STARTED")
            logger.info("=" * 80)

            # Step 1: Topic Research & Selection
            if topic:
                logger.info(f"Using provided topic: {topic}")
                selected_topic = topic
                service_focus = LENILANI_SERVICES[0]  # Default to first service
                storytelling_approach = "Direct and engaging"
                emotional_beats = ["Problem", "Solution", "Transformation"]
                cta = f"Visit {settings.company_website} to learn more"
            else:
                logger.info("Researching trending topics...")
                topics = await claude_service.research_trending_topics(focus_area=category)
                logger.info(f"Found {len(topics)} trending topics")

                logger.info("Selecting best topic for video...")
                selection = await claude_service.select_video_topic(
                    topics=topics,
                    services=LENILANI_SERVICES
                )

                selected_topic = selection.get("selected_topic", "AI for Hawaii Businesses")
                service_focus = selection.get("service_alignment", LENILANI_SERVICES[0])
                storytelling_approach = selection.get("storytelling_approach", "Emotional journey")
                emotional_beats = selection.get("emotional_beats", ["Hook", "Solution", "Impact"])
                cta = selection.get("cta", f"Visit {settings.company_website}")

            logger.info(f"Topic: {selected_topic}")
            logger.info(f"Service Focus: {service_focus}")
            logger.info(f"Storytelling Approach: {storytelling_approach}")

            # Step 2: Generate Cinematic Video Prompts
            logger.info("Generating cinematic video prompts...")
            video_prompts = await claude_service.generate_video_prompts(
                topic=selected_topic,
                service_focus=service_focus,
                storytelling_approach=storytelling_approach,
                emotional_beats=emotional_beats if isinstance(emotional_beats, list) else [emotional_beats],
                cta=cta
            )

            clip_1_prompt = video_prompts.get("clip_1_prompt")
            clip_2_prompt = video_prompts.get("clip_2_prompt")
            clip_3_prompt = video_prompts.get("clip_3_prompt")
            title_card_design = video_prompts.get("title_card_design")
            captions = video_prompts.get("captions", {})

            logger.info("Generated prompts for 3 clips + title card")
            logger.info(f"Clip 1 prompt length: {len(clip_1_prompt)} chars")
            logger.info(f"Clip 2 prompt length: {len(clip_2_prompt)} chars")
            logger.info(f"Clip 3 prompt length: {len(clip_3_prompt)} chars")

            # Step 3: Generate 3 Video Clips in Parallel
            logger.info("Generating 3 video clips in parallel with Veo 3...")
            timestamp = int(datetime.utcnow().timestamp())
            output_dir = "/tmp"

            clip_prompts = [clip_1_prompt, clip_2_prompt, clip_3_prompt]
            clips_result = await veo3_service.generate_multi_clip_video(
                clip_prompts=clip_prompts,
                output_dir=output_dir
            )

            if not clips_result.get("success"):
                error_msg = clips_result.get("error", "Unknown error generating clips")
                logger.error(f"Video clip generation failed: {error_msg}")
                errors.append(f"Video generation: {error_msg}")
                return {
                    "success": False,
                    "errors": errors,
                    "message": "Video generation failed"
                }

            clip_paths = clips_result.get("clip_paths", [])
            logger.info(f"Successfully generated {len(clip_paths)} video clips")

            # Step 4: Generate Title Card with Imagen 4
            logger.info("Generating title card image...")
            title_card_prompt = await claude_service.generate_title_card_prompt(
                topic=selected_topic,
                cta=cta
            )

            title_card_path = f"{output_dir}/title_card_{timestamp}.png"
            title_card_result = await google_image_service.generate_image(
                prompt=title_card_prompt,
                output_path=title_card_path
            )

            if not title_card_result.get("success"):
                error_msg = title_card_result.get("error", "Unknown error generating title card")
                logger.warning(f"Title card generation failed: {error_msg}")
                errors.append(f"Title card: {error_msg}")
                title_card_path = None
            else:
                title_card_path = title_card_result.get("output_path")
                logger.info(f"Title card generated: {title_card_path}")

            # Step 5: Generate Voiceover Script and Audio
            logger.info("Generating voiceover script...")
            clip_descriptions = [
                f"Clip 1: {clip_1_prompt[:100]}...",
                f"Clip 2: {clip_2_prompt[:100]}...",
                f"Clip 3: {clip_3_prompt[:100]}..."
            ]

            voiceover_script = await elevenlabs_service.generate_voiceover_script(
                topic=selected_topic,
                clip_descriptions=clip_descriptions,
                duration=settings.video_duration,
                cta=cta
            )

            logger.info(f"Voiceover script generated: {len(voiceover_script)} chars")
            logger.info(f"Script: {voiceover_script[:200]}...")

            # Generate voiceover audio
            logger.info("Generating voiceover audio with ElevenLabs...")
            voiceover_path = f"{output_dir}/voiceover_{timestamp}.mp3"

            voiceover_result = await elevenlabs_service.generate_voiceover(
                script=voiceover_script,
                output_path=voiceover_path
            )

            if not voiceover_result.get("success"):
                error_msg = voiceover_result.get("error", "Unknown error generating voiceover")
                logger.warning(f"Voiceover generation failed: {error_msg}")
                errors.append(f"Voiceover: {error_msg}")
                voiceover_path = None
            else:
                voiceover_path = voiceover_result.get("audio_path")
                logger.info(f"Voiceover audio generated: {voiceover_path}")

            # Step 6: Generate Background Music
            logger.info("Generating background music with ElevenLabs...")

            # Determine mood based on emotional beats
            if isinstance(emotional_beats, list) and len(emotional_beats) > 0:
                primary_mood = emotional_beats[0] if emotional_beats[0] in ["uplifting", "dramatic", "inspirational", "exciting"] else "uplifting"
            else:
                primary_mood = "uplifting"

            # Generate music prompt
            music_prompt_text = await elevenlabs_service.generate_music_prompt(
                topic=selected_topic,
                mood=primary_mood,
                style="corporate tech"  # Default style, can be customized
            )

            logger.info(f"Music prompt: {music_prompt_text}")

            # Generate background music
            music_path = f"{output_dir}/music_{timestamp}.mp3"
            music_result = await elevenlabs_service.generate_background_music(
                prompt=music_prompt_text,
                duration=settings.video_duration,
                output_path=music_path
            )

            if not music_result.get("success"):
                error_msg = music_result.get("error", "Unknown error generating music")
                logger.warning(f"Music generation failed: {error_msg}")
                errors.append(f"Background music: {error_msg}")
                music_path = None
            else:
                music_path = music_result.get("audio_path")
                logger.info(f"Background music generated: {music_path}")

            # Step 7: Compose Final Video (clips + title card + voiceover + music)
            logger.info("Composing final video with voiceover and music...")
            final_video_path = f"{output_dir}/final_video_{timestamp}.mp4"

            composition_result = await video_composer.compose_final_video(
                clip_paths=clip_paths,
                title_card_image_path=title_card_path,
                output_path=final_video_path,
                title_card_duration=3.0,
                voiceover_audio_path=voiceover_path,
                music_audio_path=music_path
            )

            if not composition_result.get("success"):
                error_msg = composition_result.get("error", "Unknown error composing video")
                logger.error(f"Video composition failed: {error_msg}")
                errors.append(f"Video composition: {error_msg}")
                # Fallback to just using the clips without title card
                if clip_paths:
                    logger.info("Attempting fallback composition without title card...")
                    composition_result = await video_composer.merge_clips(
                        clip_paths=clip_paths,
                        output_path=final_video_path
                    )
                    if not composition_result.get("success"):
                        return {
                            "success": False,
                            "errors": errors,
                            "message": "Video composition failed"
                        }
                else:
                    return {
                        "success": False,
                        "errors": errors,
                        "message": "Video composition failed and no fallback available"
                    }

            final_video_path = composition_result.get("output_path", final_video_path)
            logger.info(f"Final video ready: {final_video_path}")

            # Step 8: Upload to Google Drive (if requested)
            google_drive_url = None
            if publish_immediately:
                logger.info("Uploading to Google Drive...")

                # Create description with all captions
                description = f"""Topic: {selected_topic}
Service Focus: {service_focus}

Instagram Caption:
{captions.get("instagram", "N/A")}

TikTok Caption:
{captions.get("tiktok", "N/A")}

YouTube Caption:
{captions.get("youtube", "N/A")}

Twitter Caption:
{captions.get("twitter", "N/A")}
"""

                # Upload to Google Drive
                upload_result = await google_drive_uploader.upload_video(
                    video_path=final_video_path,
                    title=selected_topic,
                    description=description
                )

                if upload_result.get("success"):
                    google_drive_url = upload_result.get("url")
                    logger.info(f"Video uploaded to Google Drive: {google_drive_url}")
                else:
                    logger.error(f"Google Drive upload failed: {upload_result.get('message')}")
                    errors.append(f"Google Drive upload: {upload_result.get('message')}")

            # Step 9: Publish to YouTube via HubSpot (if credentials configured)
            youtube_url = None
            if publish_immediately and settings.hubspot_access_token:
                logger.info("Publishing to YouTube via HubSpot...")

                # Use YouTube caption if available, otherwise use topic
                youtube_description = captions.get("youtube", f"""{selected_topic}

{service_focus}

{cta}

Follow us for more AI-powered business solutions for Hawaii!

{settings.company_website}
""")

                # Extract hashtags from YouTube caption if present
                youtube_tags = []
                if "#" in youtube_description:
                    import re
                    youtube_tags = re.findall(r'#(\w+)', youtube_description)

                youtube_result = await hubspot_service.upload_and_publish_to_youtube(
                    video_path=final_video_path,
                    title=selected_topic,
                    description=youtube_description,
                    tags=youtube_tags if youtube_tags else None,
                    publish_immediately=True
                )

                if youtube_result.get("success"):
                    youtube_url = youtube_result.get("file_url")  # HubSpot file URL
                    logger.info(f"Video published to YouTube via HubSpot")
                    logger.info(f"HubSpot File URL: {youtube_url}")
                    logger.info(f"Broadcast ID: {youtube_result.get('broadcast_id')}")
                else:
                    logger.error(f"YouTube publishing failed: {youtube_result.get('message')}")
                    errors.append(f"YouTube publishing: {youtube_result.get('message')}")

            logger.info("=" * 80)
            logger.info("VIDEO GENERATION WORKFLOW COMPLETED SUCCESSFULLY")
            logger.info(f"Topic: {selected_topic}")
            logger.info(f"Clips Generated: {len(clip_paths)}")
            logger.info(f"Final Video: {final_video_path}")
            logger.info("=" * 80)

            return {
                "success": True,
                "topic": selected_topic,
                "service_focus": service_focus,
                "clip_paths": clip_paths,
                "title_card_path": title_card_path,
                "final_video_path": final_video_path,
                "captions": captions,
                "google_drive_url": google_drive_url if publish_immediately else None,
                "youtube_url": youtube_url if publish_immediately else None,
                "timestamp": datetime.utcnow().isoformat(),
                "errors": errors if errors else None
            }

        except Exception as e:
            logger.error(f"Error in video generation workflow: {e}", exc_info=True)
            errors.append(str(e))
            return {
                "success": False,
                "errors": errors,
                "message": f"Workflow failed: {str(e)}"
            }


# Global instance
video_generator = VideoGenerator()

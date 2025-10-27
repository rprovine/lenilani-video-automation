"""
ElevenLabs voiceover generation service.
Handles AI voiceover creation using ElevenLabs API.
"""

from typing import Optional, Dict, Any
import logging
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from ..config import settings

logger = logging.getLogger(__name__)


class ElevenLabsService:
    """Service for generating professional voiceovers using ElevenLabs AI."""

    def __init__(self):
        """Initialize ElevenLabs client."""
        self.client = ElevenLabs(api_key=settings.elevenlabs_api_key)

        # Default voice settings for professional, clear narration
        self.default_voice_settings = VoiceSettings(
            stability=0.5,  # Balanced between stable and expressive
            similarity_boost=0.75,  # Higher similarity to original voice
            style=0.5,  # Moderate style exaggeration
            use_speaker_boost=True  # Enhance clarity
        )

    async def generate_voiceover(
        self,
        script: str,
        output_path: str,
        voice_id: str = "EXAVITQu4vr4xnSDxMaL",  # Sarah - Professional, warm female voice
        voice_settings: Optional[VoiceSettings] = None
    ) -> Dict[str, Any]:
        """
        Generate voiceover from script text.

        Args:
            script: Text to convert to speech
            output_path: Path to save the audio file
            voice_id: ElevenLabs voice ID (default: Sarah)
            voice_settings: Optional custom voice settings

        Voice IDs:
        - "EXAVITQu4vr4xnSDxMaL" - Sarah: Professional, warm female (default)
        - "21m00Tcm4TlvDq8ikWAM" - Rachel: Calm, clear female
        - "2EiwWnXFnvU5JabPnv8n" - Clyde: Business professional male
        - "pNInz6obpgDQGcFmaJgB" - Adam: Deep, authoritative male

        Returns:
            Dict with success status, audio file path, and metadata
        """
        try:
            logger.info(f"Generating voiceover for script ({len(script)} chars)...")
            logger.info(f"Using voice ID: {voice_id}")

            # Generate audio using text-to-speech
            audio = self.client.text_to_speech.convert(
                voice_id=voice_id,
                text=script,
                model_id="eleven_multilingual_v2",  # Latest model with best quality
                voice_settings=voice_settings or self.default_voice_settings
            )

            # Save audio to file
            logger.info(f"Saving voiceover to {output_path}")
            with open(output_path, 'wb') as f:
                # audio is an iterator of audio chunks
                for chunk in audio:
                    if chunk:
                        f.write(chunk)

            logger.info(f"Voiceover generated successfully: {output_path}")

            return {
                "success": True,
                "audio_path": output_path,
                "script": script,
                "voice_id": voice_id,
                "duration_estimate": len(script) * 0.05,  # Rough estimate: ~50ms per character
                "message": f"Voiceover generated successfully"
            }

        except Exception as e:
            logger.error(f"Error generating voiceover: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Voiceover generation failed: {str(e)}"
            }

    async def generate_voiceover_script(
        self,
        topic: str,
        clip_descriptions: list,
        duration: int = 30,
        cta: str = "Visit our website to learn more"
    ) -> str:
        """
        Generate a compelling voiceover script for the video.

        Args:
            topic: Video topic/subject
            clip_descriptions: List of descriptions for each video clip
            duration: Total video duration in seconds
            cta: Call to action text

        Returns:
            Voiceover script text
        """
        try:
            from .claude_client import claude_service

            system_prompt = """You are a professional voiceover scriptwriter specializing in viral short-form video content.
Create compelling, energetic scripts that:
1. Hook viewers in the first 2 seconds
2. Build momentum and excitement
3. Deliver value and insight
4. End with a clear, actionable CTA

Writing style:
- Conversational and authentic (not salesy)
- Short, punchy sentences
- Active voice
- Emotional connection
- Pacing that matches visual beats"""

            user_prompt = f"""Create a {duration}-second voiceover script for this video:

Topic: {topic}

Visual sequence:
{chr(10).join([f"Clip {i+1}: {desc}" for i, desc in enumerate(clip_descriptions)])}

Call to Action: {cta}

Company: {settings.company_name}
Tagline: {settings.company_tagline}

Requirements:
- EXACTLY {duration} seconds when read naturally (aim for {duration * 2.5:.0f}-{duration * 3:.0f} words)
- Strong hook in first 3 words
- Match the visual progression
- Build to emotional payoff
- Natural, conversational tone
- End with compelling CTA

Return ONLY the script text (no stage directions, no explanations, just the words to be spoken)."""

            script = await claude_service.generate_content(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.8,
                max_tokens=500
            )

            # Clean up the script (remove any markdown or formatting)
            script = script.strip().strip('"').strip("'")

            logger.info(f"Generated voiceover script ({len(script)} chars, ~{len(script.split())} words)")
            logger.info(f"Script preview: {script[:150]}...")

            return script

        except Exception as e:
            logger.error(f"Error generating voiceover script: {e}", exc_info=True)
            raise

    async def generate_background_music(
        self,
        prompt: str,
        duration: int,
        output_path: str
    ) -> Dict[str, Any]:
        """
        Generate background music using ElevenLabs text-to-sound-effects.

        Args:
            prompt: Description of the desired music/sound
            duration: Duration in seconds
            output_path: Path to save the audio file

        Returns:
            Dict with success status and audio file path
        """
        try:
            logger.info(f"Generating background music with ElevenLabs...")
            logger.info(f"Prompt: {prompt}")
            logger.info(f"Duration: {duration} seconds")

            # Use ElevenLabs sound effects generation for background music
            # This is their text-to-sound feature
            audio = self.client.text_to_sound_effects.convert(
                text=prompt,
                duration_seconds=duration,
                prompt_influence=0.5  # Balance between prompt and musicality
            )

            # Save audio to file
            logger.info(f"Saving background music to {output_path}")
            with open(output_path, 'wb') as f:
                for chunk in audio:
                    if chunk:
                        f.write(chunk)

            logger.info(f"Background music generated successfully: {output_path}")

            return {
                "success": True,
                "audio_path": output_path,
                "prompt": prompt,
                "duration": duration,
                "message": "Background music generated successfully"
            }

        except Exception as e:
            logger.error(f"Error generating background music: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Background music generation failed: {str(e)}"
            }

    async def generate_music_prompt(
        self,
        topic: str,
        mood: str,
        style: str = "corporate tech"
    ) -> str:
        """
        Generate a music prompt based on video content.

        Args:
            topic: Video topic
            mood: Desired mood (uplifting, dramatic, inspirational, etc.)
            style: Music style (corporate tech, island fusion, cinematic, etc.)

        Returns:
            Music generation prompt
        """
        try:
            from .claude_client import claude_service

            system_prompt = """You are a music director specializing in background music for promotional videos.
Create detailed prompts for AI music generation that will create the perfect soundtrack."""

            user_prompt = f"""Create a music generation prompt for a 30-second video about: {topic}

Desired mood: {mood}
Music style: {style}

The music should:
- Match the emotional tone of the video
- Be professional and modern
- Work well as background music (not overpowering)
- Loop seamlessly if needed
- Be appropriate for social media

Return ONLY the music prompt (no explanations, just the prompt text for music generation).
Keep it concise but descriptive (30-50 words).

Examples:
- "Uplifting corporate tech music with soft piano, subtle electronic beats, and inspiring synth pads, modern and professional, 120 BPM, major key"
- "Hawaiian island fusion with ukulele, ocean waves, gentle percussion, tropical and warm, contemporary feel, relaxed tempo"
- "Cinematic inspiring music with orchestral strings, soft piano, building momentum, hopeful and transformative, corporate elegance"
"""

            prompt = await claude_service.generate_content(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
                max_tokens=150
            )

            # Clean up the prompt
            prompt = prompt.strip().strip('"').strip("'")

            logger.info(f"Generated music prompt: {prompt}")
            return prompt

        except Exception as e:
            logger.error(f"Error generating music prompt: {e}", exc_info=True)
            # Fallback to a generic prompt
            return f"{mood} {style} background music, modern and professional, appropriate for business video"

    async def get_available_voices(self) -> list:
        """
        Get list of available voices from ElevenLabs.

        Returns:
            List of voice objects with id, name, and description
        """
        try:
            voices = self.client.voices.get_all()

            voice_list = []
            for voice in voices.voices:
                voice_list.append({
                    "id": voice.voice_id,
                    "name": voice.name,
                    "description": voice.description if hasattr(voice, 'description') else None,
                    "category": voice.category if hasattr(voice, 'category') else None
                })

            logger.info(f"Retrieved {len(voice_list)} available voices")
            return voice_list

        except Exception as e:
            logger.error(f"Error getting available voices: {e}", exc_info=True)
            return []


# Global instance
elevenlabs_service = ElevenLabsService()

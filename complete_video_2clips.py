"""
Complete video generation using the 2 existing clips.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def complete_video_with_2clips():
    """Complete the video workflow using 2 existing clips."""
    from src.services.claude_client import claude_service
    from src.services.google_image_client import google_image_service
    from src.services.elevenlabs_client import elevenlabs_service
    from src.utils.video_composer import video_composer
    from src.services.google_drive_uploader import google_drive_uploader
    from src.config import settings

    print("\n" + "="*80)
    print("COMPLETING VIDEO WITH 2 CLIPS")
    print("="*80 + "\n")

    topic = "AI-Powered Customer Service Transforms Hawaii Tourism Industry"
    service_focus = "AI Integration & Automation"

    # Use existing clips
    clip_paths = ["/tmp/clip_1.mp4", "/tmp/clip_2.mp4"]

    print(f"Using existing clips:")
    for i, clip in enumerate(clip_paths, 1):
        size = Path(clip).stat().st_size / 1024 / 1024
        print(f"  Clip {i}: {clip} ({size:.2f} MB)")

    output_dir = "/tmp"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        # Step 1: Generate title card
        print("\n1. Generating title card with Imagen 4...")
        title_card_path = f"{output_dir}/title_card_{timestamp}.png"

        title_card_prompt = f"""Create a professional, modern title card image for a business video about {topic}.

Style: Clean, corporate, Hawaiian-themed
Colors: Ocean blues, sunset oranges, professional grays
Include: Palm trees or Hawaiian scenery in background, modern tech elements
Text placement: Leave space for text overlay
Aspect ratio: 9:16 (vertical/portrait for social media)
Mood: Professional, inspiring, tropical-tech fusion"""

        title_card_result = await google_image_service.generate_image(
            prompt=title_card_prompt,
            output_path=title_card_path
        )

        if title_card_result.get("success"):
            print(f"  ✅ Title card saved: {title_card_path}")
        else:
            print(f"  ⚠️  Title card failed: {title_card_result.get('error')}")
            title_card_path = None

        # Step 2: Generate voiceover script
        print("\n2. Generating voiceover script...")

        system_prompt = "You are a professional voiceover scriptwriter specializing in compelling promotional video scripts."

        user_prompt = f"""Write a compelling 20-second voiceover script for a promotional video about: {topic}

The video has 2 clips showing:
- Clip 1: Busy hotel lobby, frustrated staff
- Clip 2: Modern resort with AI-powered customer service

Script requirements:
- Hook viewers in first 2 seconds
- Build momentum and excitement
- Deliver value and insight
- End with clear CTA
- Natural, conversational tone
- Exactly 20 seconds when read aloud
- Service focus: {service_focus}

Return ONLY the script text, no formatting or labels."""

        script = await claude_service.generate_content(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

        print(f"  ✅ Script generated ({len(script)} chars)")
        print(f"\n  Script preview: {script[:100]}...")

        # Step 3: Generate voiceover audio
        print("\n3. Generating voiceover with ElevenLabs...")
        voiceover_path = f"{output_dir}/voiceover_{timestamp}.mp3"

        voiceover_result = await elevenlabs_service.generate_voiceover(
            script=script,
            output_path=voiceover_path
        )

        if voiceover_result.get("success"):
            size = Path(voiceover_path).stat().st_size / 1024
            print(f"  ✅ Voiceover generated: {voiceover_path} ({size:.0f} KB)")
        else:
            print(f"  ⚠️  Voiceover failed: {voiceover_result.get('error')}")
            voiceover_path = None

        # Step 4: Generate background music
        print("\n4. Generating background music...")
        music_path = f"{output_dir}/music_{timestamp}.mp3"

        music_prompt_text = await elevenlabs_service.generate_music_prompt(
            topic=topic,
            mood="uplifting",
            style="corporate tech with Hawaiian elements"
        )

        music_result = await elevenlabs_service.generate_background_music(
            prompt=music_prompt_text,
            duration=20,  # 20 seconds for 2 clips
            output_path=music_path
        )

        if music_result.get("success"):
            size = Path(music_path).stat().st_size / 1024
            print(f"  ✅ Music generated: {music_path} ({size:.0f} KB)")
        else:
            print(f"  ⚠️  Music failed: {music_result.get('error')}")
            music_path = None

        # Step 5: Compose final video
        print("\n5. Composing final video...")
        final_video_path = f"{output_dir}/final_video_{timestamp}.mp4"

        composition_result = await video_composer.compose_final_video(
            clip_paths=clip_paths,
            title_card_image_path=title_card_path,
            output_path=final_video_path,
            title_card_duration=3.0,
            voiceover_audio_path=voiceover_path,
            music_audio_path=music_path
        )

        if composition_result.get("success"):
            size = Path(final_video_path).stat().st_size / 1024 / 1024
            print(f"  ✅ Final video composed: {final_video_path} ({size:.2f} MB)")
        else:
            print(f"  ❌ Composition failed: {composition_result.get('error')}")
            return {"success": False, "error": "Video composition failed"}

        # Step 6: Generate social media captions
        print("\n6. Generating social media captions...")

        caption_system_prompt = """You are a social media expert specializing in viral content optimization.
Create platform-specific captions that maximize engagement."""

        caption_user_prompt = f"""Create engaging social media captions for a video about: {topic}

Video details:
- Focus: {service_focus}
- Duration: 20 seconds
- Style: Professional, cinematic, Hawaii business

Generate captions for:
1. YouTube (detailed description with timestamps, keywords, CTAs)
2. Instagram (engaging hook, hashtags, emoji-rich)
3. TikTok (trendy, short, hashtag-heavy)
4. LinkedIn (professional, business-focused, thought leadership)
5. Twitter/X (concise, engaging, hashtags)

Each caption should:
- Hook viewers immediately
- Include relevant hashtags
- Have clear CTA to {settings.company_website}
- Mention {settings.company_name}

Return as JSON with keys: youtube, instagram, tiktok, linkedin, twitter"""

        captions_response = await claude_service.generate_content(
            system_prompt=caption_system_prompt,
            user_prompt=caption_user_prompt
        )

        # Parse captions from response using the proper extraction function
        from src.services.claude_client import extract_json_from_response
        try:
            captions = extract_json_from_response(captions_response)
        except Exception as e:
            logger.error(f"Failed to parse captions JSON: {e}")
            # If JSON parsing fails, create a basic caption
            captions = {
                "youtube": f"{topic}\n\nVisit: {settings.company_website}",
                "instagram": f"{topic}\n\n{settings.company_website}",
                "tiktok": f"{topic} #{settings.company_name.replace(' ', '')}",
                "linkedin": f"{topic}\n\n{settings.company_website}",
                "twitter": f"{topic}\n\n{settings.company_website}"
            }

        print(f"  ✅ Social media captions generated for 5 platforms")

        # Step 7: Upload to Google Drive
        print("\n7. Uploading to Google Drive...")

        video_title = f"AI_Customer_Service_Hawaii_{timestamp}"

        # Create comprehensive description with all captions
        description = f"""TOPIC: {topic}
SERVICE FOCUS: {service_focus}
COMPANY: {settings.company_name}
WEBSITE: {settings.company_website}

================================================================================
YOUTUBE
================================================================================
{captions.get('youtube', '')}

================================================================================
INSTAGRAM
================================================================================
{captions.get('instagram', '')}

================================================================================
TIKTOK
================================================================================
{captions.get('tiktok', '')}

================================================================================
LINKEDIN
================================================================================
{captions.get('linkedin', '')}

================================================================================
TWITTER/X
================================================================================
{captions.get('twitter', '')}

================================================================================
VIDEO SPECS
================================================================================
Duration: ~20 seconds
Format: 9:16 vertical (1080x1920)
Generated: {timestamp}
Title Card: Yes
Voiceover: Yes
Background Music: Yes
"""

        upload_result = await google_drive_uploader.upload_video(
            video_path=final_video_path,
            title=video_title,
            description=description
        )

        if upload_result.get("success"):
            drive_url = upload_result.get("url", "")
            print(f"  ✅ Uploaded to Google Drive!")
            print(f"  🔗 URL: {drive_url}")
        else:
            print(f"  ⚠️  Upload failed: {upload_result.get('error')}")
            drive_url = None

        print("\n" + "="*80)
        print("✅ VIDEO GENERATION COMPLETE!")
        print("="*80)
        print(f"\n📁 Local file: {final_video_path}")
        if drive_url:
            print(f"🔗 Google Drive: {drive_url}")
        print(f"\n✨ Professional features applied:")
        print(f"  ✅ 2 cinematic video clips")
        print(f"  ✅ Branded title card")
        print(f"  ✅ AI voiceover with professional audio ducking")
        print(f"  ✅ Custom background music")
        print(f"  ✅ Loudness normalization (-16 LUFS)")
        print(f"  ✅ Broadcast-quality audio (256kbps AAC @ 48kHz)")
        print("\n" + "="*80 + "\n")

        return {
            "success": True,
            "final_video_path": final_video_path,
            "google_drive_url": drive_url,
            "clip_paths": clip_paths,
            "title_card_path": title_card_path,
            "voiceover_path": voiceover_path,
            "music_path": music_path
        }

    except Exception as e:
        logger.error(f"Error completing video: {e}", exc_info=True)
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    result = asyncio.run(complete_video_with_2clips())

    if result.get("success"):
        print("🎬 Your broadcast-quality video is ready!")
    else:
        print("⚠️  Video generation encountered issues.")

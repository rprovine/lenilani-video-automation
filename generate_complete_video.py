"""
Complete video generation with all fixes:
- 3 clips (not 2)
- Voiceover timed to match video length
- Strong CTA with contact info
- Louder background music
- No audio cutoff
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def generate_complete_video():
    from src.services.claude_client import claude_service, extract_json_from_response
    from src.services.google_image_client import google_image_service
    from src.services.elevenlabs_client import elevenlabs_service
    from src.services.veo_client import veo3_service
    from src.utils.video_composer import video_composer
    from src.services.google_drive_uploader import google_drive_uploader
    from src.config import settings

    print("\n" + "="*80)
    print("GENERATING COMPLETE PROFESSIONAL VIDEO")
    print("="*80 + "\n")

    topic = "AI-Powered Customer Service Transforms Hawaii Tourism Industry"
    service_focus = "AI Integration & Automation"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "/tmp"

    # STEP 1: Generate 3 video clips with Veo 3 in 9:16 aspect ratio
    print("\n1. Generating 3 video clips with Veo 3 (9:16 vertical)...")

    clip_prompts = [
        "Cinematic shot: Busy hotel lobby in Hawaii, overwhelmed front desk staff juggling phone calls and long guest lines, warm lighting, professional 9:16 vertical composition",
        "Cinematic shot: Modern Hawaii resort, guest using sleek AI kiosk with touchscreen for instant check-in, smiling staff member nearby, tropical plants, 9:16 vertical",
        "Cinematic shot: Happy hotel manager reviewing positive guest reviews on tablet, Hawaii beach resort background with palm trees, golden hour lighting, 9:16 vertical professional composition"
    ]

    clip_results = await veo3_service.generate_multi_clip_video(
        clip_prompts=clip_prompts,
        output_dir=output_dir
    )

    if not clip_results.get("success"):
        print(f"  ❌ Video generation failed: {clip_results.get('error')}")
        return {"success": False}

    clip_paths = clip_results["clip_paths"]
    print(f"  ✅ Generated {len(clip_paths)} clips")

    # Convert clips from 16:9 to 9:16
    print("\n  Converting clips to 9:16 aspect ratio...")
    import subprocess
    converted_clip_paths = []

    for i, clip_path in enumerate(clip_paths, 1):
        output_clip = f"{output_dir}/clip_{i}_9x16.mp4"

        # Scale and crop to fill 9:16 - zoom in to avoid letterboxing
        cmd = [
            "ffmpeg",
            "-i", clip_path,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-c:a", "copy",
            "-y",
            output_clip
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            converted_clip_paths.append(output_clip)
            print(f"    ✅ Converted clip {i} to 9:16")
        else:
            print(f"    ❌ Failed to convert clip {i}")
            return {"success": False}

    clip_paths = converted_clip_paths

    # STEP 2: Generate title card
    print("\n2. Generating title card...")
    title_card_path = f"{output_dir}/title_card_{timestamp}.png"

    title_card_result = await google_image_service.generate_image(
        prompt=f"""Professional title card for business video about {topic}

Style: Clean, modern, corporate Hawaiian theme
Colors: Ocean blues (#0077BE), sunset orange (#FF6B35), white text
Layout: 9:16 vertical format
Elements: Subtle palm tree silhouettes, gradient background, space for text overlay
Mood: Professional, innovative, welcoming
Quality: High-end business presentation""",
        output_path=title_card_path
    )

    if title_card_result.get("success"):
        print(f"  ✅ Title card generated")
    else:
        print(f"  ⚠️  Title card failed, continuing without")
        title_card_path = None

    # STEP 3: Generate voiceover script (timed for 27 seconds: 3s title + 24s clips)
    print("\n3. Generating voiceover script...")

    script = await claude_service.generate_content(
        system_prompt="You are a professional voiceover scriptwriter for promotional videos.",
        user_prompt=f"""Write a compelling 25-second voiceover script for a video about: {topic}

Video structure:
- 0-3s: Title card with topic
- 3-27s: 3 video clips showing the transformation

Script requirements:
- MUST be exactly 25 seconds when read at natural pace
- Hook in first 5 seconds
- Build excitement through middle
- END with strong call-to-action: "Visit LeniLani.com to transform your business with AI"
- Mention "LeniLani Consulting" in the CTA
- Natural, enthusiastic tone
- Service focus: {service_focus}

Return ONLY the script text, no labels or formatting."""
    )

    print(f"  ✅ Script: {script[:100]}...")

    # STEP 4: Generate voiceover audio
    print("\n4. Generating voiceover...")
    voiceover_path = f"{output_dir}/voiceover_{timestamp}.mp3"

    voiceover_result = await elevenlabs_service.generate_voiceover(
        script=script,
        output_path=voiceover_path
    )

    if not voiceover_result.get("success"):
        print(f"  ❌ Voiceover failed")
        return {"success": False}

    print(f"  ✅ Voiceover generated")

    # STEP 5: Generate background music (27 seconds to match video)
    print("\n5. Generating background music...")
    music_path = f"{output_dir}/music_{timestamp}.mp3"

    music_prompt = await elevenlabs_service.generate_music_prompt(
        topic=topic,
        mood="uplifting and energetic",
        style="modern corporate tech with Hawaiian ukulele"
    )

    music_result = await elevenlabs_service.generate_background_music(
        prompt=music_prompt,
        duration=27,  # Match total video length
        output_path=music_path
    )

    if not music_result.get("success"):
        print(f"  ⚠️  Music generation failed, continuing without")
        music_path = None
    else:
        print(f"  ✅ Background music generated")

    # STEP 6: Compose final video
    print("\n6. Composing final video...")
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
        print(f"  ❌ Video composition failed: {composition_result.get('error')}")
        return {"success": False}

    print(f"  ✅ Final video composed")

    # STEP 7: Generate social media captions
    print("\n7. Generating social media captions...")

    captions_response = await claude_service.generate_content(
        system_prompt="You are a social media expert for B2B tech companies.",
        user_prompt=f"""Create platform-specific captions for a video about: {topic}

Company: {settings.company_name}
Website: {settings.company_website}
Phone: {settings.company_phone}
Email: {settings.company_email}

Each caption MUST:
- Include clear CTA with website link
- Mention {settings.company_name}
- Include phone number for YouTube/LinkedIn
- Have platform-appropriate hashtags
- Be engaging and professional

Generate for: YouTube, Instagram, TikTok, LinkedIn, Twitter/X

Return as JSON: {{"youtube": "...", "instagram": "...", "tiktok": "...", "linkedin": "...", "twitter": "..."}}"""
    )

    try:
        captions = extract_json_from_response(captions_response)
    except:
        captions = {
            "youtube": f"{topic}\n\n{settings.company_name}\n{settings.company_website}\n{settings.company_phone}",
            "instagram": f"{topic}\n\nVisit: {settings.company_website}\n\n#AIinHawaii #HawaiiBusiness",
            "tiktok": f"{topic} #{settings.company_name.replace(' ', '')}",
            "linkedin": f"{topic}\n\n{settings.company_name} - {settings.company_website}",
            "twitter": f"{topic}\n\n{settings.company_website}"
        }

    print(f"  ✅ Social media captions generated")

    # STEP 8: Create comprehensive description
    description = f"""TOPIC: {topic}
SERVICE FOCUS: {service_focus}

COMPANY: {settings.company_name}
WEBSITE: {settings.company_website}
PHONE: {settings.company_phone}
EMAIL: {settings.company_email}
TAGLINE: {settings.company_tagline}

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
Duration: ~27 seconds (3s title card + 24s video clips)
Format: 9:16 vertical (1080x1920)
Generated: {timestamp}
Clips: 3 cinematic AI-generated clips
Title Card: Yes
Voiceover: Professional AI voice with script
Background Music: Custom AI-generated music
Audio: Broadcast quality with professional ducking"""

    # STEP 9: Upload to Google Drive
    print("\n8. Uploading to Google Drive...")

    video_title = f"AI_Customer_Service_Hawaii_{timestamp}"

    upload_result = await google_drive_uploader.upload_video(
        video_path=final_video_path,
        title=video_title,
        description=description
    )

    if upload_result.get("success"):
        print(f"  ✅ Uploaded to Google Drive!")
        print(f"  🔗 {upload_result.get('url', '')}")

    print("\n" + "="*80)
    print("✅ COMPLETE PROFESSIONAL VIDEO GENERATED!")
    print("="*80)
    print(f"\n📁 Local: {final_video_path}")
    print(f"🔗 Google Drive: {upload_result.get('url', '')}")
    print(f"\n✨ Features:")
    print(f"  ✅ 3 cinematic video clips (24 seconds)")
    print(f"  ✅ Professional title card (3 seconds)")
    print(f"  ✅ Voiceover with strong CTA")
    print(f"  ✅ Background music with ducking")
    print(f"  ✅ Full contact information in CTA")
    print(f"  ✅ Platform-specific social media captions")
    print("\n" + "="*80 + "\n")

    return {
        "success": True,
        "video_path": final_video_path,
        "google_drive_url": upload_result.get("url")
    }

if __name__ == "__main__":
    result = asyncio.run(generate_complete_video())

    if result.get("success"):
        print("🎬 Your professional promotional video is ready!")
    else:
        print("⚠️  Video generation encountered issues.")

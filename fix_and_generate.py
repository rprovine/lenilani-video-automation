"""
Fix existing 16:9 clips and regenerate video with proper 9:16 aspect ratio.
"""
import asyncio
from pathlib import Path

async def main():
    from src.services.claude_client import claude_service
    from src.services.google_image_client import google_image_service
    from src.services.elevenlabs_client import elevenlabs_service
    from src.utils.video_composer import video_composer
    from src.services.google_drive_uploader import google_drive_uploader
    from src.config import settings
    from datetime import datetime
    import subprocess
    
    print("\n" + "="*80)
    print("FIXING ASPECT RATIO AND REGENERATING VIDEO")
    print("="*80 + "\n")
    
    topic = "AI-Powered Customer Service Transforms Hawaii Tourism Industry"
    service_focus = "AI Integration & Automation"
    
    # Convert existing 1280x720 clips to 1080x1920 (crop and scale to fill)
    print("Converting clips to 9:16 aspect ratio...")
    
    for i in [1, 2]:
        input_clip = f"/tmp/clip_{i}.mp4"
        output_clip = f"/tmp/clip_{i}_9x16.mp4"
        
        # Scale and crop to fill 9:16 - zoom in to avoid letterboxing
        cmd = [
            "ffmpeg",
            "-i", input_clip,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-c:a", "copy",
            "-y",
            output_clip
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ Converted clip {i} to 9:16")
        else:
            print(f"  ❌ Failed to convert clip {i}: {result.stderr}")
            return
    
    # Use the converted clips
    clip_paths = ["/tmp/clip_1_9x16.mp4", "/tmp/clip_2_9x16.mp4"]
    
    output_dir = "/tmp"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate title card
    print("\n1. Generating title card...")
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
        print(f"  ✅ Title card saved")
    else:
        print(f"  ⚠️  Title card failed")
        title_card_path = None
    
    # Generate voiceover
    print("\n2. Generating voiceover...")
    script = await claude_service.generate_content(
        system_prompt="You are a professional voiceover scriptwriter.",
        user_prompt=f"""Write a compelling 20-second voiceover script for: {topic}
        
The video has 2 clips. Requirements:
- Hook viewers immediately
- Natural, conversational tone
- Exactly 20 seconds when read aloud
- Service focus: {service_focus}

Return ONLY the script text."""
    )
    
    print(f"  ✅ Script generated")
    
    voiceover_path = f"{output_dir}/voiceover_{timestamp}.mp3"
    voiceover_result = await elevenlabs_service.generate_voiceover(
        script=script,
        output_path=voiceover_path
    )
    
    if voiceover_result.get("success"):
        print(f"  ✅ Voiceover generated")
    else:
        print(f"  ⚠️  Voiceover failed")
        voiceover_path = None
    
    # Generate music
    print("\n3. Generating background music...")
    music_path = f"{output_dir}/music_{timestamp}.mp3"
    music_prompt_text = await elevenlabs_service.generate_music_prompt(
        topic=topic,
        mood="uplifting",
        style="corporate tech with Hawaiian elements"
    )
    
    music_result = await elevenlabs_service.generate_background_music(
        prompt=music_prompt_text,
        duration=20,
        output_path=music_path
    )
    
    if music_result.get("success"):
        print(f"  ✅ Music generated")
    else:
        print(f"  ⚠️  Music failed")
        music_path = None
    
    # Compose video
    print("\n4. Composing final video...")
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
        print(f"  ✅ Final video composed: {final_video_path}")
    else:
        print(f"  ❌ Composition failed")
        return
    
    # Generate captions
    print("\n5. Generating social media captions...")
    from src.services.claude_client import extract_json_from_response
    
    captions_response = await claude_service.generate_content(
        system_prompt="You are a social media expert specializing in viral content optimization.",
        user_prompt=f"""Create engaging social media captions for a video about: {topic}

Generate captions for: YouTube, Instagram, TikTok, LinkedIn, Twitter/X
Each caption should hook viewers, include hashtags, and have CTA to {settings.company_website}

Return as JSON with keys: youtube, instagram, tiktok, linkedin, twitter"""
    )
    
    try:
        captions = extract_json_from_response(captions_response)
    except:
        captions = {}
    
    print(f"  ✅ Captions generated")
    
    # Upload to Google Drive
    print("\n6. Uploading to Google Drive...")
    video_title = f"AI_Customer_Service_Hawaii_{timestamp}"
    
    description = f"""TOPIC: {topic}
SERVICE FOCUS: {service_focus}
COMPANY: {settings.company_name}
WEBSITE: {settings.company_website}

YOUTUBE: {captions.get('youtube', '')}
INSTAGRAM: {captions.get('instagram', '')}
TIKTOK: {captions.get('tiktok', '')}
LINKEDIN: {captions.get('linkedin', '')}
TWITTER: {captions.get('twitter', '')}

Duration: ~20 seconds
Format: 9:16 vertical (1080x1920)
Generated: {timestamp}"""
    
    upload_result = await google_drive_uploader.upload_video(
        video_path=final_video_path,
        title=video_title,
        description=description
    )
    
    if upload_result.get("success"):
        print(f"  ✅ Uploaded to Google Drive!")
        print(f"  🔗 URL: {upload_result.get('url', '')}")
    
    print("\n" + "="*80)
    print("✅ VIDEO COMPLETE WITH PROPER 9:16 ASPECT RATIO!")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())

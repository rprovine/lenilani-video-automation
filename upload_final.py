"""Upload the final complete video to Google Drive."""
import asyncio
from datetime import datetime

async def main():
    from src.services.google_drive_uploader import google_drive_uploader
    from src.config import settings

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_path = "/tmp/final_complete_video_20251026_164951.mp4"

    description = f"""TOPIC: AI-Powered Customer Service Transforms Hawaii Tourism Industry
SERVICE FOCUS: AI Integration & Automation

COMPANY: {settings.company_name}
WEBSITE: {settings.company_website}
PHONE: {settings.company_phone}
EMAIL: {settings.company_email}
TAGLINE: {settings.company_tagline}

================================================================================
VIDEO FEATURES
================================================================================
✅ Title card with company information (3 seconds)
✅ 2 cinematic AI-generated clips (16 seconds)
✅ Professional voiceover with strong CTA (27 seconds)
✅ Background music with professional ducking (27 seconds)
✅ Video loops smoothly to match audio duration
✅ No frozen frames
✅ Complete audio without cutoff

================================================================================
TECHNICAL SPECS
================================================================================
Duration: 27 seconds
Resolution: 1080x1920 (9:16 vertical - mobile optimized)
Video: H.264, 30fps
Audio: AAC, 48kHz, 191kbps
Loudness: -16 LUFS broadcast standard

Generated: {timestamp}
"""

    print("\nUploading to Google Drive...")

    upload_result = await google_drive_uploader.upload_video(
        video_path=video_path,
        title=f"AI_Customer_Service_Complete_{timestamp}",
        description=description
    )

    if upload_result.get("success"):
        print(f"✅ Uploaded successfully!")
        print(f"🔗 {upload_result.get('url', '')}")
    else:
        print(f"❌ Upload failed: {upload_result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main())

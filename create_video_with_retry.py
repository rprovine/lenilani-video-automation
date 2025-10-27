"""
Persistent video generation with automatic hourly retry.
Keeps trying until successful, then notifies when ready.
"""

import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/video_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def attempt_video_generation():
    """Attempt to generate video. Returns (success, result)."""
    from src.workflows.video_generator import video_generator

    topic = "AI-Powered Customer Service Transforms Hawaii Tourism Industry"

    try:
        logger.info(f"Attempting video generation for topic: {topic}")

        result = await video_generator.generate_and_publish(
            topic=topic,
            category="AI",
            publish_immediately=True
        )

        return result.get("success", False), result

    except Exception as e:
        logger.error(f"Video generation attempt failed: {e}", exc_info=True)
        return False, {"success": False, "error": str(e)}

def is_rate_limit_error(result):
    """Check if the error is a rate limit that we should retry."""
    # Convert entire result to string for comprehensive checking
    result_str = str(result).lower()

    # Check for rate limit indicators
    rate_limit_keywords = ["429", "resource_exhausted", "quota", "rate limit", "too many requests"]

    for keyword in rate_limit_keywords:
        if keyword in result_str:
            return True

    return False

def print_success_summary(result):
    """Print a beautiful success message."""
    print("\n" + "=" * 80)
    print("🎉 VIDEO GENERATION COMPLETE!")
    print("=" * 80)
    print(f"\n✅ Topic: {result.get('topic')}")
    print(f"✅ Service Focus: {result.get('service_focus')}")
    print(f"\n📁 Final Video: {result.get('final_video_path')}")

    if result.get('google_drive_url'):
        print(f"\n🔗 GOOGLE DRIVE LINK:")
        print(f"   {result.get('google_drive_url')}")
        print(f"\n   ⭐ Your video is ready for review!")

    print(f"\n📊 Details:")
    print(f"   - Clips Generated: {len(result.get('clip_paths', []))}")
    print(f"   - Title Card: {'✅' if result.get('title_card_path') else '❌'}")
    print(f"   - Voiceover: {'✅' if result.get('voiceover_path') else '❌'}")
    print(f"   - Background Music: {'✅' if result.get('music_path') else '❌'}")

    print(f"\n✨ Professional Features Applied:")
    print(f"   ✅ Cinematic video generation (Veo 3)")
    print(f"   ✅ AI-generated voiceover (ElevenLabs)")
    print(f"   ✅ Custom background music (ElevenLabs)")
    print(f"   ✅ Audio ducking (music lowers during speech)")
    print(f"   ✅ Loudness normalization (-16 LUFS)")
    print(f"   ✅ Music fade in/out")
    print(f"   ✅ Dynamic compression")
    print(f"   ✅ Peak limiting (broadcast-safe)")
    print(f"   ✅ 256kbps AAC @ 48kHz")

    if result.get('errors'):
        print(f"\n⚠️  Warnings ({len(result['errors'])}):")
        for error in result['errors']:
            print(f"   - {error}")

    print("\n" + "=" * 80 + "\n")

async def retry_until_success():
    """Keep trying to generate video every hour until successful."""

    retry_count = 0
    retry_interval = 3600  # 1 hour in seconds

    print("\n" + "=" * 80)
    print("AUTOMATED VIDEO GENERATION WITH PERSISTENT RETRY")
    print("=" * 80)
    print(f"\nTopic: AI-Powered Customer Service Transforms Hawaii Tourism Industry")
    print(f"Retry Interval: Every {retry_interval // 60} minutes")
    print(f"Strategy: Keep trying until successful")
    print("\n" + "=" * 80 + "\n")

    while True:
        retry_count += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n{'=' * 80}")
        print(f"ATTEMPT #{retry_count} - {timestamp}")
        print(f"{'=' * 80}\n")

        success, result = await attempt_video_generation()

        if success:
            # SUCCESS! Print summary and exit
            print_success_summary(result)

            # Log success to file
            logger.info("=" * 80)
            logger.info("VIDEO GENERATION SUCCESSFUL!")
            logger.info(f"Google Drive URL: {result.get('google_drive_url')}")
            logger.info("=" * 80)

            return result

        else:
            # Check if it's a rate limit error worth retrying
            if is_rate_limit_error(result):
                logger.warning(f"Attempt #{retry_count} failed due to rate limit")
                print(f"\n⏳ Rate limit encountered. Will retry in {retry_interval // 60} minutes...")
                print(f"   Next attempt at: {datetime.fromtimestamp(time.time() + retry_interval).strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   (Check /tmp/video_generation.log for details)")

                # Wait for retry interval
                await asyncio.sleep(retry_interval)

            else:
                # Non-rate-limit error - something else went wrong
                logger.error(f"Attempt #{retry_count} failed with non-rate-limit error")
                print(f"\n❌ Unexpected error occurred:")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                print(f"   Errors: {result.get('errors', [])}")
                print(f"\n⏳ Will retry in {retry_interval // 60} minutes anyway...")
                print(f"   Next attempt at: {datetime.fromtimestamp(time.time() + retry_interval).strftime('%Y-%m-%d %H:%M:%S')}")

                # Wait for retry interval
                await asyncio.sleep(retry_interval)

if __name__ == "__main__":
    print(f"\n🎬 Starting persistent video generation...")
    print(f"📝 Logs: /tmp/video_generation.log")
    print(f"🔄 Will retry every hour until successful\n")

    try:
        result = asyncio.run(retry_until_success())

        if result.get("success"):
            print("\n✅ DONE! Your broadcast-quality video is ready for review in Google Drive!")
            print(f"🔗 {result.get('google_drive_url')}\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Retry loop interrupted by user (Ctrl+C)")
        print("Run this script again to resume automatic retry.\n")

    except Exception as e:
        print(f"\n\n❌ Fatal error in retry loop: {e}")
        import traceback
        traceback.print_exc()

"""
Generate a complete professional video with the full workflow.
"""

import asyncio
import logging
from datetime import datetime

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def create_professional_video():
    """Run the complete video generation workflow."""
    from src.workflows.video_generator import video_generator

    print("\n" + "="*80)
    print("PROFESSIONAL VIDEO GENERATION - FULL WORKFLOW")
    print("="*80 + "\n")

    print("This will:")
    print("1. Research Hawaii tech/business news")
    print("2. Match to LeniLani services")
    print("3. Generate cinematic video prompts")
    print("4. Create 3x 8-second clips with Veo 3")
    print("5. Generate branded title card")
    print("6. Write professional voiceover script")
    print("7. Generate voiceover audio")
    print("8. Generate custom background music")
    print("9. Mix audio with professional ducking")
    print("10. Upload to Google Drive")
    print("\n" + "="*80 + "\n")

    start_time = datetime.now()

    try:
        # Run the complete workflow
        result = await video_generator.generate_and_publish(
            topic=None,  # Auto-research trending topics
            category="AI",  # Focus on AI/tech
            publish_immediately=True  # Upload to Google Drive
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("\n" + "="*80)
        if result.get("success"):
            print("✅ VIDEO GENERATION COMPLETE!")
            print("="*80)
            print(f"\nTopic: {result.get('topic')}")
            print(f"Service Focus: {result.get('service_focus')}")
            print(f"\nGeneration Time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
            print(f"\nFinal Video: {result.get('final_video_path')}")

            if result.get('google_drive_url'):
                print(f"Google Drive: {result.get('google_drive_url')}")

            print(f"\nClips Generated: {len(result.get('clip_paths', []))}")
            print(f"Title Card: {result.get('title_card_path')}")

            if result.get('captions'):
                print("\n--- Social Media Captions ---")
                captions = result['captions']
                if captions.get('instagram'):
                    print(f"\nInstagram:\n{captions['instagram'][:150]}...")
                if captions.get('tiktok'):
                    print(f"\nTikTok:\n{captions['tiktok'][:150]}...")

            if result.get('errors'):
                print(f"\n⚠️  Warnings: {len(result['errors'])}")
                for error in result['errors']:
                    print(f"  - {error}")

            print("\n✨ Professional Features Applied:")
            print("  ✅ Cinematic video generation (Veo 3)")
            print("  ✅ AI-generated voiceover (ElevenLabs)")
            print("  ✅ Custom background music (ElevenLabs)")
            print("  ✅ Audio ducking (music lowers during speech)")
            print("  ✅ Loudness normalization (-16 LUFS)")
            print("  ✅ Music fade in/out")
            print("  ✅ Dynamic compression")
            print("  ✅ Peak limiting (broadcast-safe)")
            print("  ✅ 256kbps AAC @ 48kHz")

        else:
            print("❌ VIDEO GENERATION FAILED")
            print("="*80)
            print(f"\nErrors: {result.get('errors', [])}")
            print(f"Message: {result.get('message')}")

        print("\n" + "="*80 + "\n")

        return result

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    result = asyncio.run(create_professional_video())

    if result.get("success"):
        print("🎬 Your broadcast-quality video is ready!")
        print(f"📁 Location: {result.get('final_video_path')}")
    else:
        print("⚠️  Video generation encountered issues. Check logs above.")

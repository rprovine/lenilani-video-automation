"""
Generate 3 portrait video clips using updated Veo 3 client.
"""
import asyncio
from src.services.veo_client import veo3_service
from datetime import datetime

async def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("\n" + "="*80)
    print("GENERATING 3 PORTRAIT VIDEO CLIPS (9:16)")
    print("="*80 + "\n")

    # Video prompts for the clips
    clip_prompts = [
        # Clip 1: Overwhelmed business owner
        """Cinematic portrait video (9:16 vertical): A stressed small business owner in Hawaii sits at a desk surrounded by stacks of paperwork and ringing phones. The camera slowly zooms in on their overwhelmed expression. Warm natural lighting from a window. Professional office setting with tropical plants visible. High-quality commercial cinematography, shallow depth of field, 8 seconds.""",

        # Clip 2: Discovery of AI solution
        """Cinematic portrait video (9:16 vertical): Hawaiian business owner having an enlightened moment while looking at a laptop screen showing LeniLani Consulting website. Their expression changes from curious to excited. Modern office with ocean view through window. Bright, hopeful lighting. Professional commercial quality, smooth camera movement, 8 seconds.""",

        # Clip 3: AI transformation success
        """Cinematic portrait video (9:16 vertical): Same Hawaiian business owner now relaxed and confident, working efficiently on a sleek laptop with a modern AI dashboard visible on screen. Bright, clean office with organized workspace. Camera pans to show satisfied customers in background. Professional commercial quality, vibrant colors, success story aesthetic, 8 seconds."""
    ]

    for i, prompt in enumerate(clip_prompts, 1):
        print(f"\n{'='*80}")
        print(f"GENERATING CLIP {i}/3")
        print(f"{'='*80}\n")
        print(f"Prompt: {prompt[:150]}...\n")

        output_path = f"/tmp/clip_{i}_portrait_{timestamp}.mp4"

        result = await veo3_service.generate_video_clip(
            prompt=prompt,
            duration=8,
            output_path=output_path,
            aspect_ratio="9:16"  # PORTRAIT MODE
        )

        if result.get("success"):
            print(f"\n✅ Clip {i} generated successfully!")
            print(f"📁 Output: {output_path}\n")
        else:
            print(f"\n❌ Clip {i} failed: {result.get('error')}")
            print(f"Message: {result.get('message')}\n")
            return False

    print("\n" + "="*80)
    print("✅ ALL PORTRAIT CLIPS GENERATED SUCCESSFULLY!")
    print("="*80 + "\n")
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)

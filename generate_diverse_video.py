"""
Generate a complete video with diverse topics and proper Problem → Solution → CTA structure.
"""
import asyncio
import subprocess
from datetime import datetime
from src.utils.topic_generator import topic_generator
from src.services.veo_client import veo3_service
from src.config import settings
import os
from elevenlabs.client import ElevenLabs

async def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("\n" + "="*80)
    print("GENERATING DIVERSE VIDEO WITH PROBLEM → SOLUTION → CTA")
    print("="*80 + "\n")

    # Step 1: Generate unique concept
    print("1. Generating unique video concept...")
    concept = topic_generator.generate_video_concept()

    print(f"\n   Business: {concept['business_type'].upper()}")
    print(f"   Location: {concept['location']}, Hawaii")
    print(f"   Problem: {concept['problem']['title']}")
    print(f"   CTA: {concept['cta_main']}")
    print(f"   ✅ Concept generated\n")

    # Step 2: Generate 3 portrait video clips
    print("2. Generating 3 portrait video clips (this takes ~5-10 minutes)...\n")

    clip_paths = []
    for i, prompt_key in enumerate(['clip_1_prompt', 'clip_2_prompt', 'clip_3_prompt'], 1):
        print(f"   Generating Clip {i}/3...")
        prompt = concept[prompt_key]
        output_path = f"/tmp/clip_{i}_diverse_{timestamp}.mp4"

        result = await veo3_service.generate_video_clip(
            prompt=prompt,
            duration=8,
            output_path=output_path,
            aspect_ratio="9:16"
        )

        if result.get("success"):
            # Convert to portrait if needed
            converted_path = f"/tmp/clip_{i}_portrait_diverse_{timestamp}.mp4"
            subprocess.run([
                "ffmpeg", "-i", output_path,
                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
                "-c:a", "copy", "-y", converted_path
            ], capture_output=True)
            clip_paths.append(converted_path)
            print(f"   ✅ Clip {i} generated\n")
        else:
            print(f"   ❌ Clip {i} failed: {result.get('error')}")
            return False

    # Step 3: Generate voiceover
    print("3. Generating custom voiceover...")
    client = ElevenLabs(api_key=settings.elevenlabs_api_key)

    voiceover_path = f"/tmp/voiceover_{timestamp}.mp3"
    audio = client.text_to_speech.convert(
        text=concept['voiceover_script'],
        voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice ID
        model_id="eleven_multilingual_v2"
    )

    with open(voiceover_path, 'wb') as f:
        for chunk in audio:
            f.write(chunk)
    print(f"   ✅ Voiceover generated\n")

    # Step 4: Select random Hawaiian music from library
    print("4. Selecting random Hawaiian music from library...")
    from src.services.music_library import music_library

    music_result = music_library.select_random_segment(
        output_path=f"/tmp/music_segment_{timestamp}.mp3",
        segment_duration=35
    )

    if music_result["success"]:
        music_path = music_result["path"]
        print(f"   ✅ Selected: {music_result['source_file']}")
        print(f"   ✅ Segment: {music_result['start_time']:.1f}s - {music_result['start_time'] + 35:.1f}s\n")
    else:
        raise Exception(f"Failed to select music: {music_result.get('error')}")

    # Step 5: Add text overlays to clips
    print("5. Adding Instagram-style text overlays...")
    clips_with_text = []

    text_overlays = [
        (concept['clip_1_text'], "white", "#FF6B35"),
        (concept['clip_2_text'], "#FFD700", "white"),
        (concept['clip_3_text'], "#00D9FF", "white")
    ]

    for i, (clip_path, (text, color1, color2)) in enumerate(zip(clip_paths, text_overlays), 1):
        output_path = f"/tmp/clip_{i}_with_text_{timestamp}.mp4"
        words = text.split()
        line1 = ' '.join(words[:len(words)//2])
        line2 = ' '.join(words[len(words)//2:])

        subprocess.run([
            "ffmpeg", "-i", clip_path,
            "-vf", f"drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:text='{line1}':fontcolor={color1}:fontsize=90:x=(w-text_w)/2:y=200:borderw=5:bordercolor=black:box=1:boxcolor=black@0.6:boxborderw=20,drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:text='{line2}':fontcolor={color2}:fontsize=90:x=(w-text_w)/2:y=320:borderw=5:bordercolor=black:box=1:boxcolor=black@0.6:boxborderw=20",
            "-c:a", "copy", "-y", output_path
        ], capture_output=True)
        clips_with_text.append(output_path)
    print(f"   ✅ Text overlays added\n")

    # Step 6: Create modern intro title card
    print("6. Creating modern intro title card...")
    intro_card_path = f"/tmp/intro_card_{timestamp}.mp4"
    subprocess.run([
        "ffmpeg", "-f", "lavfi", "-i", "color=c=#0A2E4D:s=1080x1920:d=3",
        "-vf",
        # Smooth gradient background
        "drawbox=x=0:y=0:w=1080:h=640:color=#0A2E4D@1.0:t=fill,"
        "drawbox=x=0:y=640:w=1080:h=640:color=#1B5E8C@0.9:t=fill,"
        "drawbox=x=0:y=1280:w=1080:h=640:color=#2A9D8F@0.8:t=fill,"
        # White accent line (centered vertically)
        "drawbox=x=90:y=1030:w=900:h=8:color=white@0.8:t=fill,"
        # Main title - Bold and clean (centered around y=960)
        "drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:"
        "text='LENILANI':"
        "fontcolor=white:"
        "fontsize=140:"
        "x=(w-text_w)/2:"
        "y=770:"
        "borderw=0,"
        # Subtitle
        "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:"
        "text='CONSULTING':"
        "fontcolor=#FFD700:"
        "fontsize=70:"
        "x=(w-text_w)/2:"
        "y=930:"
        "borderw=0,"
        # Tagline
        "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:"
        "text='AI Solutions for Hawaii Business':"
        "fontcolor=white@0.9:"
        "fontsize=48:"
        "x=(w-text_w)/2:"
        "y=1080:"
        "borderw=0",
        "-c:v", "libx264", "-t", "3", "-pix_fmt", "yuv420p", "-y", intro_card_path
    ], capture_output=True)
    print(f"   ✅ Modern intro card created\n")

    # Step 7: Create modern CTA outro card
    print("7. Creating modern CTA outro card...")
    outro_card_path = f"/tmp/outro_cta_{timestamp}.mp4"

    # Split hook into lines if needed
    hook_words = concept['cta']['hook'].split()
    hook_line1 = ' '.join(hook_words[:2]) if len(hook_words) > 2 else concept['cta']['hook']
    hook_line2 = ' '.join(hook_words[2:]) if len(hook_words) > 2 else ''

    subprocess.run([
        "ffmpeg", "-f", "lavfi", "-i", "color=c=#0A2E4D:s=1080x1920:d=6",
        "-vf",
        # Gradient background
        "drawbox=x=0:y=0:w=1080:h=960:color=#0A2E4D@1.0:t=fill,"
        "drawbox=x=0:y=960:w=1080:h=960:color=#1B5E8C@0.95:t=fill,"
        # Accent bars (centered around y=960)
        "drawbox=x=0:y=680:w=1080:h=6:color=#2A9D8F@0.9:t=fill,"
        "drawbox=x=0:y=1240:w=1080:h=6:color=#2A9D8F@0.9:t=fill,"
        # CTA Hook - Bold (centered vertically around y=960)
        f"drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:"
        f"text='{hook_line1}':"
        f"fontcolor=white:"
        f"fontsize=95:"
        f"x=(w-text_w)/2:"
        f"y=710:"
        f"borderw=0,"
        f"drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:"
        f"text='{hook_line2 if hook_line2 else concept['cta']['action'].split()[0]}':"
        f"fontcolor=#FFD700:"
        f"fontsize=110:"
        f"x=(w-text_w)/2:"
        f"y=820:"
        f"borderw=0,"
        # Primary action
        f"drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:"
        f"text='{concept['cta_main']}':"
        f"fontcolor=white:"
        f"fontsize=58:"
        f"x=(w-text_w)/2:"
        f"y=960:"
        f"borderw=0,"
        # Website - Prominent
        "drawbox=x=240:y=1050:w=600:h=100:color=#2A9D8F@0.2:t=fill,"
        "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:"
        "text='LeniLani.com':"
        "fontcolor=#00D9FF:"
        "fontsize=80:"
        "x=(w-text_w)/2:"
        "y=1070:"
        "borderw=0,"
        # Phone
        "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:"
        "text='808-766-1164':"
        "fontcolor=white:"
        "fontsize=60:"
        "x=(w-text_w)/2:"
        "y=1180:"
        "borderw=0,"
        # Urgency
        f"drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:"
        f"text='{concept['cta_urgency']}':"
        f"fontcolor=#FF6B35:"
        f"fontsize=48:"
        f"x=(w-text_w)/2:"
        f"y=1300:"
        f"borderw=0",
        "-c:v", "libx264", "-t", "6", "-pix_fmt", "yuv420p", "-y", outro_card_path
    ], capture_output=True)
    print(f"   ✅ Modern CTA outro created\n")

    # Step 8: Concatenate all parts
    print("8. Assembling complete video...")
    concat_file = f"/tmp/concat_{timestamp}.txt"
    with open(concat_file, 'w') as f:
        f.write(f"file '{intro_card_path}'\n")
        for clip in clips_with_text:
            f.write(f"file '{clip}'\n")
        f.write(f"file '{outro_card_path}'\n")

    video_parts_path = f"/tmp/video_parts_{timestamp}.mp4"
    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file,
        "-c", "copy", "-y", video_parts_path
    ], capture_output=True)
    print(f"   ✅ Video parts assembled\n")

    # Step 9: Mix audio (voiceover + Hawaiian music) - music continues after voiceover
    print("9. Mixing audio...")
    audio_final_path = f"/tmp/audio_final_{timestamp}.m4a"
    subprocess.run([
        "ffmpeg",
        "-i", voiceover_path,
        "-i", music_path,
        "-filter_complex", "[0:a]volume=1.5[vo];[1:a]volume=0.2[music];[vo][music]amix=inputs=2:duration=longest[out]",
        "-map", "[out]", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
        "-t", "35", "-y", audio_final_path
    ], capture_output=True)
    print(f"   ✅ Audio mixed\n")

    # Step 10: Final video with audio and fade (both video AND audio)
    print("10. Creating final video with smooth fade out...")
    final_output = f"/tmp/DIVERSE_VIDEO_{timestamp}.mp4"
    subprocess.run([
        "ffmpeg",
        "-stream_loop", "-1", "-i", video_parts_path,
        "-i", audio_final_path,
        "-t", "35",
        "-filter_complex",
        "[0:v]fade=t=out:st=33:d=2[vfade];"
        "[1:a]afade=t=out:st=33:d=2[afade]",
        "-map", "[vfade]", "-map", "[afade]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-c:a", "aac", "-b:a", "256k", "-y", final_output
    ], capture_output=True)

    print(f"\n{'='*80}")
    print("✅ COMPLETE!")
    print(f"{'='*80}\n")
    print(f"📁 Final video: {final_output}")
    print(f"\n📊 Video Details:")
    print(f"   Business: {concept['business_type'].title()}")
    print(f"   Problem: {concept['problem']['title']}")
    print(f"   CTA: {concept['cta_main']}")

    # Get specs
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=width,height:format=duration", "-of", "default=noprint_wrappers=1", final_output],
        capture_output=True, text=True
    )
    print(f"\n📐 Specs:\n{probe.stdout}")

    return final_output

if __name__ == "__main__":
    final_video = asyncio.run(main())
    if final_video:
        subprocess.run(["open", final_video])

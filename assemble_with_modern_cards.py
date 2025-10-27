"""
Assemble complete video with NEW modern cards and authentic Hawaiian music.
"""
import subprocess
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

print("\n" + "="*80)
print("ASSEMBLING COMPLETE VIDEO WITH MODERN DESIGN")
print("="*80 + "\n")

# Step 1: Add text overlays to the 3 clips
print("1. Adding text overlays to clips...")

clips_with_text = []

# Clip 1: "DROWNING IN PAPERWORK"
print("   Adding text to Clip 1...")
subprocess.run([
    "ffmpeg", "-i", "/tmp/clip_1_portrait_diverse_20251026_174911.mp4",
    "-vf", "drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:text='DROWNING IN':fontcolor=white:fontsize=90:x=(w-text_w)/2:y=200:borderw=5:bordercolor=black:box=1:boxcolor=black@0.6:boxborderw=20,drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:text='PAPERWORK?':fontcolor=#FF6B35:fontsize=90:x=(w-text_w)/2:y=320:borderw=5:bordercolor=black:box=1:boxcolor=black@0.6:boxborderw=20",
    "-c:a", "copy", "-y", f"/tmp/clip_1_text_{timestamp}.mp4"
], capture_output=True)
clips_with_text.append(f"/tmp/clip_1_text_{timestamp}.mp4")
print("   ✅ Clip 1 text added")

# Clip 2: "AI POWERED SOLUTION"
print("   Adding text to Clip 2...")
subprocess.run([
    "ffmpeg", "-i", "/tmp/clip_2_portrait_diverse_20251026_174911.mp4",
    "-vf", "drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:text='AI POWERED':fontcolor=#FFD700:fontsize=90:x=(w-text_w)/2:y=200:borderw=5:bordercolor=black:box=1:boxcolor=black@0.6:boxborderw=20,drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:text='SOLUTION':fontcolor=white:fontsize=90:x=(w-text_w)/2:y=320:borderw=5:bordercolor=black:box=1:boxcolor=black@0.6:boxborderw=20",
    "-c:a", "copy", "-y", f"/tmp/clip_2_text_{timestamp}.mp4"
], capture_output=True)
clips_with_text.append(f"/tmp/clip_2_text_{timestamp}.mp4")
print("   ✅ Clip 2 text added")

# Clip 3: "READY FOR CHANGE?"
print("   Adding text to Clip 3...")
subprocess.run([
    "ffmpeg", "-i", "/tmp/clip_3_portrait_diverse_20251026_174911.mp4",
    "-vf", "drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:text='READY FOR':fontcolor=#00D9FF:fontsize=90:x=(w-text_w)/2:y=200:borderw=5:bordercolor=black:box=1:boxcolor=black@0.6:boxborderw=20,drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:text='CHANGE?':fontcolor=white:fontsize=90:x=(w-text_w)/2:y=320:borderw=5:bordercolor=black:box=1:boxcolor=black@0.6:boxborderw=20",
    "-c:a", "copy", "-y", f"/tmp/clip_3_text_{timestamp}.mp4"
], capture_output=True)
clips_with_text.append(f"/tmp/clip_3_text_{timestamp}.mp4")
print("   ✅ Clip 3 text added\n")

# Step 2: Concatenate all parts with NEW modern cards
print("2. Assembling all video parts with modern cards...")
concat_file = f"/tmp/concat_{timestamp}.txt"
with open(concat_file, 'w') as f:
    # Use the NEW modern intro card
    f.write(f"file '/tmp/modern_intro_card_20251026_180624.mp4'\n")
    for clip in clips_with_text:
        f.write(f"file '{clip}'\n")
    # Use the NEW modern outro card
    f.write(f"file '/tmp/modern_outro_card_20251026_180624.mp4'\n")

video_parts_path = f"/tmp/video_all_parts_{timestamp}.mp4"
subprocess.run([
    "ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file,
    "-c", "copy", "-y", video_parts_path
], capture_output=True)
print("   ✅ All parts concatenated\n")

# Step 3: Select random music from library
print("3. Selecting random Hawaiian music from library...")
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

# Step 4: Prepare audio mix
print("4. Mixing audio...")

# Check for existing voiceover
import os
voiceover_files = [f for f in os.listdir('/tmp') if f.startswith('voiceover_') and f.endswith('.mp3')]

if voiceover_files:
    voiceover_path = f"/tmp/{sorted(voiceover_files)[-1]}"

    audio_final_path = f"/tmp/audio_final_{timestamp}.m4a"
    subprocess.run([
        "ffmpeg",
        "-i", voiceover_path,
        "-i", music_path,
        "-filter_complex", "[0:a]volume=1.5[vo];[1:a]volume=0.2[music];[vo][music]amix=inputs=2:duration=longest[out]",
        "-map", "[out]", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
        "-t", "35", "-y", audio_final_path
    ], capture_output=True)
    print("   ✅ Audio mixed\n")

    # Step 5: Final video with audio and fade
    print("5. Creating final video with modern design...")
    final_output = f"/tmp/MODERN_COMPLETE_VIDEO_{timestamp}.mp4"
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
else:
    # No audio available - just video
    print("   ⚠️  No voiceover found - creating video-only\n")
    print("5. Creating final video...")
    final_output = f"/tmp/MODERN_COMPLETE_VIDEO_{timestamp}.mp4"
    subprocess.run([
        "ffmpeg",
        "-i", video_parts_path,
        "-t", "35",
        "-filter_complex", "[0:v]fade=t=out:st=32:d=3[vfade]",
        "-map", "[vfade]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-y", final_output
    ], capture_output=True)

print(f"\n{'='*80}")
print("✅ COMPLETE VIDEO WITH MODERN DESIGN READY!")
print(f"{'='*80}\n")
print(f"📁 Final video: {final_output}")

# Get specs
probe = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries",
     "stream=width,height:format=duration", "-of", "default=noprint_wrappers=1", final_output],
    capture_output=True, text=True
)
print(f"\n📊 Specs:\n{probe.stdout}")

print("\n" + "="*80)
print("VIDEO STRUCTURE WITH MODERN DESIGN:")
print("="*80)
print("1. NEW Modern Intro Card - Centered & Clean (3 seconds)")
print("2. Clip 1: PROBLEM - Drowning in Paperwork (8 seconds)")
print("3. Clip 2: SOLUTION - AI Powered Solution (8 seconds)")
print("4. Clip 3: CTA HOOK - Ready for Change? (8 seconds)")
print("5. NEW Modern Outro CTA - Centered Contact Info (6 seconds)")
print("6. Fade out (3 seconds)")
print("\nNEW FEATURES:")
print("• Bold, clean typography (no borders)")
print("• Professional gradient backgrounds")
print("• Vertically centered text")
print("• Authentic Hawaiian music (pahu drums, ipu, ukulele)")
print("="*80 + "\n")

# Open the video
subprocess.run(["open", final_output])

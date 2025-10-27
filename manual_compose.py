"""
Manually compose a complete video with all components working correctly.
"""
import subprocess
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

print("\n" + "="*80)
print("MANUALLY COMPOSING COMPLETE VIDEO")
print("="*80 + "\n")

# Step 1: Create title card video (3 seconds) with text overlay
print("1. Creating title card video with company info...")
title_card_cmd = [
    "ffmpeg",
    "-loop", "1",
    "-i", "/tmp/title_card_20251026_164000.png",
    "-vf", (
        "scale=1080:1920:force_original_aspect_ratio=decrease,"
        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,"
        "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:text='AI-Powered Customer Service':"
        "fontcolor=white:fontsize=60:x=(w-text_w)/2:y=400:borderw=3:bordercolor=black,"
        "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:text='Transforms Hawaii Tourism':"
        "fontcolor=white:fontsize=60:x=(w-text_w)/2:y=500:borderw=3:bordercolor=black,"
        "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='LeniLani Consulting':"
        "fontcolor=#FF6B35:fontsize=48:x=(w-text_w)/2:y=1200:borderw=2:bordercolor=black,"
        "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='LeniLani.com':"
        "fontcolor=white:fontsize=42:x=(w-text_w)/2:y=1300:borderw=2:bordercolor=black,"
        "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='(808) 555-0123':"
        "fontcolor=white:fontsize=38:x=(w-text_w)/2:y=1380:borderw=2:bordercolor=black"
    ),
    "-c:v", "libx264",
    "-t", "3",
    "-pix_fmt", "yuv420p",
    "-r", "30",
    "-y",
    "/tmp/title_card_video.mp4"
]

result = subprocess.run(title_card_cmd, capture_output=True, text=True)
if result.returncode == 0:
    print("  ✅ Title card video created")
else:
    print(f"  ❌ Title card failed: {result.stderr[-500:]}")
    exit(1)

# Step 2: Concatenate title card + 2 clips
print("\n2. Concatenating title card and clips...")

# Create concat file
concat_content = """file '/tmp/title_card_video.mp4'
file '/tmp/clip_1_9x16.mp4'
file '/tmp/clip_2_9x16.mp4'
"""

with open("/tmp/concat_list.txt", "w") as f:
    f.write(concat_content)

concat_cmd = [
    "ffmpeg",
    "-f", "concat",
    "-safe", "0",
    "-i", "/tmp/concat_list.txt",
    "-c", "copy",
    "-y",
    "/tmp/video_concat.mp4"
]

result = subprocess.run(concat_cmd, capture_output=True, text=True)
if result.returncode == 0:
    print("  ✅ Video clips concatenated")
else:
    print(f"  ❌ Concat failed: {result.stderr[-500:]}")
    exit(1)

# Step 3: Extend/loop music to match voiceover duration (27 seconds)
print("\n3. Extending background music to 27 seconds...")

music_extend_cmd = [
    "ffmpeg",
    "-stream_loop", "1",  # Loop once
    "-i", "/tmp/music_20251026_164000.mp3",
    "-t", "27",
    "-y",
    "/tmp/music_extended.mp3"
]

result = subprocess.run(music_extend_cmd, capture_output=True, text=True)
if result.returncode == 0:
    print("  ✅ Music extended to 27 seconds")
else:
    print(f"  ❌ Music extend failed: {result.stderr[-500:]}")
    exit(1)

# Step 4: Mix voiceover and music with professional ducking
print("\n4. Mixing audio with ducking...")

audio_mix_cmd = [
    "ffmpeg",
    "-i", "/tmp/voiceover_20251026_164000.mp3",
    "-i", "/tmp/music_extended.mp3",
    "-filter_complex",
    (
        # Split voiceover for sidechain and mix
        "[0:a]asplit=2[vo1][vo2];"

        # Prepare music with volume
        "[1:a]volume=0.4[music_raw];"

        # Duck music when voiceover speaks
        "[vo1][music_raw]sidechaincompress=threshold=0.03:ratio=4:attack=20:release=250:level_sc=1[music_ducked];"

        # Mix voiceover and ducked music
        "[vo2][music_ducked]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[mixed];"

        # Final polish
        "[mixed]loudnorm=I=-16:TP=-1.5:LRA=11,acompressor=threshold=-20dB:ratio=3:attack=5:release=50:makeup=2dB[out]"
    ),
    "-map", "[out]",
    "-c:a", "aac",
    "-b:a", "256k",
    "-ar", "48000",
    "-y",
    "/tmp/audio_final.m4a"
]

result = subprocess.run(audio_mix_cmd, capture_output=True, text=True)
if result.returncode == 0:
    print("  ✅ Audio mixed with ducking")
else:
    print(f"  ❌ Audio mix failed: {result.stderr[-500:]}")
    exit(1)

# Step 5: Loop video to match audio duration (27 seconds)
print("\n5. Extending video to match audio duration...")

video_extend_cmd = [
    "ffmpeg",
    "-stream_loop", "-1",  # Loop indefinitely
    "-i", "/tmp/video_concat.mp4",
    "-t", "27",
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "23",
    "-pix_fmt", "yuv420p",
    "-y",
    "/tmp/video_extended.mp4"
]

result = subprocess.run(video_extend_cmd, capture_output=True, text=True)
if result.returncode == 0:
    print("  ✅ Video extended to 27 seconds")
else:
    print(f"  ❌ Video extend failed: {result.stderr[-500:]}")
    exit(1)

# Step 6: Combine video and audio
print("\n6. Combining video and audio...")

final_output = f"/tmp/final_complete_video_{timestamp}.mp4"

combine_cmd = [
    "ffmpeg",
    "-i", "/tmp/video_extended.mp4",
    "-i", "/tmp/audio_final.m4a",
    "-c:v", "copy",
    "-c:a", "copy",
    "-map", "0:v:0",
    "-map", "1:a:0",
    "-y",
    final_output
]

result = subprocess.run(combine_cmd, capture_output=True, text=True)
if result.returncode == 0:
    print("  ✅ Final video created!")
    print(f"\n📁 Output: {final_output}")

    # Get final specs
    probe_cmd = ["ffprobe", "-v", "error", "-show_entries",
                 "format=duration:stream=width,height", "-of", "default=noprint_wrappers=1",
                 final_output]
    probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
    print(f"\n✅ Video specs:\n{probe_result.stdout}")

else:
    print(f"  ❌ Combine failed: {result.stderr[-500:]}")
    exit(1)

print("\n" + "="*80)
print("✅ COMPLETE VIDEO READY!")
print("="*80 + "\n")

"""
Create proper video with:
- 2 clips in 9:16 (centered properly)
- End card with contact information
- Full audio with music
"""
import subprocess
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

print("\n" + "="*80)
print("CREATING PROPER VIDEO WITH END CARD")
print("="*80 + "\n")

# Step 1: Check clip dimensions and re-center if needed
print("1. Analyzing and fixing clip aspect ratios...")

for i in [1, 2]:
    input_clip = f"/tmp/clip_{i}.mp4"
    output_clip = f"/tmp/clip_{i}_centered.mp4"

    # Scale to fill 9:16 and center the content (not just crop edges)
    # This will zoom and position to keep the important content centered
    cmd = [
        "ffmpeg",
        "-i", input_clip,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "copy",
        "-y",
        output_clip
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✅ Clip {i} centered for 9:16")
    else:
        print(f"  ❌ Failed to process clip {i}")
        exit(1)

# Step 2: Create attractive end card with contact info
print("\n2. Creating end card with contact information...")

end_card_cmd = [
    "ffmpeg",
    "-f", "lavfi",
    "-i", "color=c=#0077BE:s=1080x1920:d=5",  # 5 second blue background
    "-vf", (
        # Gradient overlay
        "drawbox=x=0:y=0:w=1080:h=1920:color=#0077BE@1:t=fill,"

        # Main heading
        "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:"
        "text='Ready to Transform Your Business?':"
        "fontcolor=white:fontsize=58:x=(w-text_w)/2:y=300:borderw=2:bordercolor=black,"

        # Subheading
        "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:"
        "text='AI-Powered Solutions for Hawaii':"
        "fontcolor=#FF6B35:fontsize=48:x=(w-text_w)/2:y=400:borderw=2:bordercolor=black,"

        # Company name (larger)
        "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:"
        "text='LeniLani Consulting':"
        "fontcolor=white:fontsize=68:x=(w-text_w)/2:y=700:borderw=3:bordercolor=black,"

        # Website (prominent)
        "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:"
        "text='LeniLani.com':"
        "fontcolor=#FFD700:fontsize=72:x=(w-text_w)/2:y=850:borderw=3:bordercolor=black,"

        # Phone
        "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:"
        "text='Call: (808) 555-0123':"
        "fontcolor=white:fontsize=52:x=(w-text_w)/2:y=1050:borderw=2:bordercolor=black,"

        # Email
        "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:"
        "text='hello@lenilani.com':"
        "fontcolor=white:fontsize=48:x=(w-text_w)/2:y=1150:borderw=2:bordercolor=black,"

        # CTA
        "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:"
        "text='Contact Us Today!':"
        "fontcolor=#FF6B35:fontsize=58:x=(w-text_w)/2:y=1400:borderw=3:bordercolor=black"
    ),
    "-c:v", "libx264",
    "-t", "5",
    "-pix_fmt", "yuv420p",
    "-y",
    "/tmp/end_card.mp4"
]

result = subprocess.run(end_card_cmd, capture_output=True, text=True)
if result.returncode == 0:
    print("  ✅ End card created")
else:
    print(f"  ❌ End card failed: {result.stderr[-500:]}")
    exit(1)

# Step 3: Concatenate clips + end card
print("\n3. Concatenating clips and end card...")

concat_content = """file '/tmp/clip_1_centered.mp4'
file '/tmp/clip_2_centered.mp4'
file '/tmp/end_card.mp4'
"""

with open("/tmp/concat_list_final.txt", "w") as f:
    f.write(concat_content)

concat_cmd = [
    "ffmpeg",
    "-f", "concat",
    "-safe", "0",
    "-i", "/tmp/concat_list_final.txt",
    "-c", "copy",
    "-y",
    "/tmp/video_with_endcard.mp4"
]

result = subprocess.run(concat_cmd, capture_output=True, text=True)
if result.returncode == 0:
    print("  ✅ Video concatenated")
else:
    print(f"  ❌ Concat failed: {result.stderr[-500:]}")
    exit(1)

# Step 4: Extend music to match new duration (16 + 5 = 21 seconds for video, voiceover is ~27s)
print("\n4. Preparing audio mix...")

# Use voiceover duration (27s) and extend music to match
music_extend_cmd = [
    "ffmpeg",
    "-stream_loop", "1",
    "-i", "/tmp/music_20251026_164000.mp3",
    "-t", "27",
    "-y",
    "/tmp/music_extended_final.mp3"
]

result = subprocess.run(music_extend_cmd, capture_output=True, text=True)
if result.returncode == 0:
    print("  ✅ Music extended to 27 seconds")
else:
    print(f"  ❌ Music extend failed")
    exit(1)

# Step 5: Mix voiceover and music with ducking
print("\n5. Mixing audio with ducking...")

audio_mix_cmd = [
    "ffmpeg",
    "-i", "/tmp/voiceover_20251026_164000.mp3",
    "-i", "/tmp/music_extended_final.mp3",
    "-filter_complex",
    (
        "[0:a]asplit=2[vo1][vo2];"
        "[1:a]volume=0.5[music_raw];"  # Increased to 50% for more audible music
        "[vo1][music_raw]sidechaincompress=threshold=0.03:ratio=4:attack=20:release=250:level_sc=1[music_ducked];"
        "[vo2][music_ducked]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[mixed];"
        "[mixed]loudnorm=I=-16:TP=-1.5:LRA=11,acompressor=threshold=-20dB:ratio=3:attack=5:release=50:makeup=2dB[out]"
    ),
    "-map", "[out]",
    "-c:a", "aac",
    "-b:a", "256k",
    "-ar", "48000",
    "-y",
    "/tmp/audio_mixed_final.m4a"
]

result = subprocess.run(audio_mix_cmd, capture_output=True, text=True)
if result.returncode == 0:
    print("  ✅ Audio mixed")
else:
    print(f"  ❌ Audio mix failed")
    exit(1)

# Step 6: Loop video to match audio duration (27 seconds)
print("\n6. Extending video to match audio...")

video_extend_cmd = [
    "ffmpeg",
    "-stream_loop", "-1",
    "-i", "/tmp/video_with_endcard.mp4",
    "-t", "27",
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "23",
    "-pix_fmt", "yuv420p",
    "-y",
    "/tmp/video_extended_final.mp4"
]

result = subprocess.run(video_extend_cmd, capture_output=True, text=True)
if result.returncode == 0:
    print("  ✅ Video extended to 27 seconds")
else:
    print(f"  ❌ Video extend failed")
    exit(1)

# Step 7: Combine final video and audio
print("\n7. Creating final video...")

final_output = f"/tmp/complete_final_video_{timestamp}.mp4"

combine_cmd = [
    "ffmpeg",
    "-i", "/tmp/video_extended_final.mp4",
    "-i", "/tmp/audio_mixed_final.m4a",
    "-c:v", "copy",
    "-c:a", "copy",
    "-map", "0:v:0",
    "-map", "1:a:0",
    "-y",
    final_output
]

result = subprocess.run(combine_cmd, capture_output=True, text=True)
if result.returncode == 0:
    print(f"  ✅ Final video created!")
    print(f"\n📁 Output: {final_output}")

    # Get specs
    probe_cmd = ["ffprobe", "-v", "error", "-show_entries",
                 "format=duration:stream=width,height", "-of", "default=noprint_wrappers=1",
                 final_output]
    probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
    print(f"\n✅ Video specs:\n{probe_result.stdout}")
else:
    print(f"  ❌ Combine failed")
    exit(1)

print("\n" + "="*80)
print("✅ COMPLETE VIDEO WITH END CARD READY!")
print("="*80 + "\n")

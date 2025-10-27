"""
Assemble complete portrait video with:
- Intro title card
- 3 clips with Instagram text overlays
- Outro card
- Hawaiian music + voiceover
- Fade-out
"""
import subprocess
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

print("\n" + "="*80)
print("ASSEMBLING COMPLETE PORTRAIT VIDEO")
print("="*80 + "\n")

# Step 1: Add Instagram-style text overlays to clips
print("1. Adding Instagram text overlays to clips...")

clips_with_text = []

# Clip 1: "OVERWHELMED BY CUSTOMERS?"
cmd1 = [
    "ffmpeg", "-i", "/tmp/clip_1_9x16_20251026_173850.mp4",
    "-vf", "drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:text='OVERWHELMED':fontcolor=white:fontsize=90:x=(w-text_w)/2:y=200:borderw=5:bordercolor=black:box=1:boxcolor=black@0.6:boxborderw=20,drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:text='BY CUSTOMERS?':fontcolor=#FF6B35:fontsize=90:x=(w-text_w)/2:y=320:borderw=5:bordercolor=black:box=1:boxcolor=black@0.6:boxborderw=20",
    "-c:a", "copy", "-y", f"/tmp/clip_1_with_text_{timestamp}.mp4"
]
subprocess.run(cmd1, capture_output=True)
clips_with_text.append(f"/tmp/clip_1_with_text_{timestamp}.mp4")
print("  ✅ Clip 1 text added")

# Clip 2: "DISCOVER AI SOLUTION"
cmd2 = [
    "ffmpeg", "-i", "/tmp/clip_2_9x16_20251026_173850.mp4",
    "-vf", "drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:text='DISCOVER':fontcolor=#FFD700:fontsize=90:x=(w-text_w)/2:y=200:borderw=5:bordercolor=black:box=1:boxcolor=black@0.6:boxborderw=20,drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:text='AI SOLUTION':fontcolor=white:fontsize=90:x=(w-text_w)/2:y=320:borderw=5:bordercolor=black:box=1:boxcolor=black@0.6:boxborderw=20",
    "-c:a", "copy", "-y", f"/tmp/clip_2_with_text_{timestamp}.mp4"
]
subprocess.run(cmd2, capture_output=True)
clips_with_text.append(f"/tmp/clip_2_with_text_{timestamp}.mp4")
print("  ✅ Clip 2 text added")

# Clip 3: "AI-POWERED TRANSFORMATION"
cmd3 = [
    "ffmpeg", "-i", "/tmp/clip_3_9x16_20251026_173850.mp4",
    "-vf", "drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:text='AI-POWERED':fontcolor=#00D9FF:fontsize=90:x=(w-text_w)/2:y=200:borderw=5:bordercolor=black:box=1:boxcolor=black@0.6:boxborderw=20,drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:text='TRANSFORMATION':fontcolor=white:fontsize=90:x=(w-text_w)/2:y=320:borderw=5:bordercolor=black:box=1:boxcolor=black@0.6:boxborderw=20",
    "-c:a", "copy", "-y", f"/tmp/clip_3_with_text_{timestamp}.mp4"
]
subprocess.run(cmd3, capture_output=True)
clips_with_text.append(f"/tmp/clip_3_with_text_{timestamp}.mp4")
print("  ✅ Clip 3 text added")

# Step 2: Create outro card with contact info
print("\n2. Creating outro card...")
outro_cmd = [
    "ffmpeg", "-f", "lavfi", "-i", "color=c=#0077BE:s=1080x1920:d=5",
    "-vf", "drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:text='Ready to Transform?':fontcolor=white:fontsize=75:x=(w-text_w)/2:y=600:borderw=4:bordercolor=black,drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:text='LeniLani Consulting':fontcolor=#FFD700:fontsize=85:x=(w-text_w)/2:y=750:borderw=4:bordercolor=black,drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:text='LeniLani.com':fontcolor=#00D9FF:fontsize=90:x=(w-text_w)/2:y=900:borderw=3:bordercolor=black,drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:text='808-766-1164':fontcolor=white:fontsize=75:x=(w-text_w)/2:y=1050:borderw=3:bordercolor=black,drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='AI Integration for Hawaii':fontcolor=white:fontsize=55:x=(w-text_w)/2:y=1200:borderw=2:bordercolor=black",
    "-c:v", "libx264", "-t", "5", "-pix_fmt", "yuv420p", "-y", f"/tmp/outro_card_{timestamp}.mp4"
]
subprocess.run(outro_cmd, capture_output=True)
print("  ✅ Outro card created")

# Step 3: Concatenate all video parts
print("\n3. Concatenating all video parts...")
concat_file = f"/tmp/concat_list_{timestamp}.txt"
with open(concat_file, 'w') as f:
    f.write(f"file '/tmp/title_card_final_portrait.mp4'\n")
    for clip in clips_with_text:
        f.write(f"file '{clip}'\n")
    f.write(f"file '/tmp/outro_card_{timestamp}.mp4'\n")

concat_cmd = [
    "ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file,
    "-c", "copy", "-y", f"/tmp/video_all_parts_{timestamp}.mp4"
]
subprocess.run(concat_cmd, capture_output=True)
print(f"  ✅ Video concatenated")

# Step 4: Loop background music to match total duration (3s intro + 24s clips + 5s outro = 32s)
print("\n4. Preparing Hawaiian music...")
music_cmd = [
    "ffmpeg", "-stream_loop", "-1", "-i", "/tmp/hawaiian_music_20251026_173047.mp3",
    "-t", "32", "-y", f"/tmp/hawaiian_music_looped_{timestamp}.mp3"
]
subprocess.run(music_cmd, capture_output=True)
print("  ✅ Music looped to 32 seconds")

# Step 5: Mix Hawaiian music with voiceover
print("\n5. Mixing audio...")
# Voiceover at 150%, Hawaiian music at 20% for authentic but subtle background
audio_mix_cmd = [
    "ffmpeg",
    "-i", "/tmp/voiceover_20251026_164000.mp3",
    "-i", f"/tmp/hawaiian_music_looped_{timestamp}.mp3",
    "-filter_complex", "[0:a]volume=1.5[vo];[1:a]volume=0.2[music];[vo][music]amerge=inputs=2,pan=stereo|c0<c0+c2|c1<c1+c3[out]",
    "-map", "[out]", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
    "-y", f"/tmp/audio_final_{timestamp}.m4a"
]
subprocess.run(audio_mix_cmd, capture_output=True)
print("  ✅ Audio mixed")

# Step 6: Loop video to match audio duration and add fade-out
print("\n6. Creating final video with audio and fade...")
final_output = f"/tmp/FINAL_PORTRAIT_VIDEO_{timestamp}.mp4"
final_cmd = [
    "ffmpeg",
    "-stream_loop", "-1", "-i", f"/tmp/video_all_parts_{timestamp}.mp4",
    "-i", f"/tmp/audio_final_{timestamp}.m4a",
    "-t", "32",
    "-filter_complex", "[0:v]fade=t=out:st=29:d=3[vfade]",
    "-map", "[vfade]", "-map", "1:a:0",
    "-c:v", "libx264", "-preset", "medium", "-crf", "23",
    "-c:a", "copy", "-y", final_output
]
subprocess.run(final_cmd, capture_output=True)

print(f"\n✅ COMPLETE!")
print(f"📁 Final video: {final_output}")

# Get specs
probe = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries",
     "stream=width,height:format=duration", "-of", "default=noprint_wrappers=1", final_output],
    capture_output=True, text=True
)
print(f"\n📊 Specs:\n{probe.stdout}")

print("\n" + "="*80)
print("✅ COMPLETE PORTRAIT VIDEO READY!")
print("="*80 + "\n")

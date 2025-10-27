"""
Assemble complete demo video using existing clips with full sequencing.
"""
import subprocess
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

print("\n" + "="*80)
print("ASSEMBLING COMPLETE DEMO VIDEO")
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

# Step 2: Create powerful CTA outro card
print("2. Creating CTA outro card...")
subprocess.run([
    "ffmpeg", "-f", "lavfi", "-i", "color=c=#0077BE:s=1080x1920:d=6",
    "-vf", "drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:text='READY FOR CHANGE?':fontcolor=white:fontsize=80:x=(w-text_w)/2:y=500:borderw=5:bordercolor=black,drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:text='Book Your Free AI Consultation':fontcolor=#FFD700:fontsize=75:x=(w-text_w)/2:y=700:borderw=4:bordercolor=black,drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:text='LeniLani.com':fontcolor=#00D9FF:fontsize=85:x=(w-text_w)/2:y=900:borderw=3:bordercolor=black,drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:text='808-766-1164':fontcolor=white:fontsize=75:x=(w-text_w)/2:y=1050:borderw=3:bordercolor=black,drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='Limited Spots Available This Month':fontcolor=#FF6B35:fontsize=60:x=(w-text_w)/2:y=1250:borderw=3:bordercolor=black",
    "-c:v", "libx264", "-t", "6", "-pix_fmt", "yuv420p", "-y", f"/tmp/outro_cta_{timestamp}.mp4"
], capture_output=True)
print("   ✅ CTA outro created\n")

# Step 3: Concatenate all parts (intro + 3 clips + outro)
print("3. Assembling all video parts...")
concat_file = f"/tmp/concat_{timestamp}.txt"
with open(concat_file, 'w') as f:
    f.write(f"file '/tmp/title_card_final_portrait.mp4'\n")  # Intro
    for clip in clips_with_text:
        f.write(f"file '{clip}'\n")
    f.write(f"file '/tmp/outro_cta_{timestamp}.mp4'\n")  # Outro

video_parts_path = f"/tmp/video_all_parts_{timestamp}.mp4"
subprocess.run([
    "ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file,
    "-c", "copy", "-y", video_parts_path
], capture_output=True)
print("   ✅ All parts concatenated\n")

# Step 4: Prepare audio (use existing Hawaiian music and voiceover if available)
print("4. Preparing audio mix...")

# Check for existing audio files
import os
voiceover_files = [f for f in os.listdir('/tmp') if f.startswith('voiceover_') and f.endswith('.mp3')]
music_files = [f for f in os.listdir('/tmp') if f.startswith('hawaiian_music_') and f.endswith('.mp3')]

if voiceover_files and music_files:
    voiceover_path = f"/tmp/{sorted(voiceover_files)[-1]}"
    music_path = f"/tmp/{sorted(music_files)[-1]}"

    audio_final_path = f"/tmp/audio_final_{timestamp}.m4a"
    subprocess.run([
        "ffmpeg",
        "-i", voiceover_path,
        "-i", music_path,
        "-filter_complex", "[0:a]volume=1.5[vo];[1:a]volume=0.2[music];[vo][music]amerge=inputs=2,pan=stereo|c0<c0+c2|c1<c1+c3[out]",
        "-map", "[out]", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
        "-t", "35", "-y", audio_final_path
    ], capture_output=True)
    print("   ✅ Audio mixed\n")

    # Step 5: Final video with audio and fade
    print("5. Creating final video with audio and fade...")
    final_output = f"/tmp/DEMO_COMPLETE_VIDEO_{timestamp}.mp4"
    subprocess.run([
        "ffmpeg",
        "-stream_loop", "-1", "-i", video_parts_path,
        "-i", audio_final_path,
        "-t", "35",
        "-filter_complex", "[0:v]fade=t=out:st=32:d=3[vfade]",
        "-map", "[vfade]", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-c:a", "copy", "-y", final_output
    ], capture_output=True)
else:
    # No audio available - just video
    print("   ⚠️  No audio files found - creating video-only\n")
    print("5. Creating final video...")
    final_output = f"/tmp/DEMO_COMPLETE_VIDEO_{timestamp}.mp4"
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
print("✅ COMPLETE DEMO VIDEO READY!")
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
print("VIDEO STRUCTURE:")
print("="*80)
print("1. Intro Title Card (3 seconds)")
print("2. Clip 1: PROBLEM - Drowning in Paperwork (8 seconds)")
print("3. Clip 2: SOLUTION - AI Powered Solution (8 seconds)")
print("4. Clip 3: CTA HOOK - Ready for Change? (8 seconds)")
print("5. Outro CTA Card - Contact Info & Urgency (6 seconds)")
print("6. Fade out (3 seconds)")
print("="*80 + "\n")

# Open the video
subprocess.run(["open", final_output])

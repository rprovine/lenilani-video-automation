"""
Create modern, professional intro and outro cards for social media.
Based on 2025 design trends: bold typography, gradients, centralized composition.
"""
import subprocess
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

print("\n" + "="*80)
print("CREATING MODERN INTRO & OUTRO CARDS")
print("="*80 + "\n")

# Modern Intro Card - Bold Typography with Animated Gradient
print("1. Creating modern intro card...")

intro_output = f"/tmp/modern_intro_card_{timestamp}.mp4"

# Create intro with:
# - Smooth gradient background (ocean blues to tropical greens)
# - Bold, clean typography
# - Subtle animation feel
subprocess.run([
    "ffmpeg", "-f", "lavfi", "-i", "color=c=#0A2E4D:s=1080x1920:d=3",
    "-vf",
    # Create gradient overlay (dark blue to teal)
    "drawbox=x=0:y=0:w=1080:h=640:color=#0A2E4D@1.0:t=fill,"
    "drawbox=x=0:y=640:w=1080:h=640:color=#1B5E8C@0.9:t=fill,"
    "drawbox=x=0:y=1280:w=1080:h=640:color=#2A9D8F@0.8:t=fill,"
    # Add white accent line
    "drawbox=x=90:y=880:w=900:h=8:color=white@0.8:t=fill,"
    # Main title - BOLD and CLEAN
    "drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:"
    "text='LENILANI':"
    "fontcolor=white:"
    "fontsize=140:"
    "x=(w-text_w)/2:"
    "y=650:"
    "borderw=0,"
    # Subtitle - Professional
    "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:"
    "text='CONSULTING':"
    "fontcolor=#FFD700:"
    "fontsize=70:"
    "x=(w-text_w)/2:"
    "y=800:"
    "borderw=0,"
    # Tagline - Clean
    "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:"
    "text='AI Solutions for Hawaii Business':"
    "fontcolor=white@0.9:"
    "fontsize=48:"
    "x=(w-text_w)/2:"
    "y=1000:"
    "borderw=0",
    "-c:v", "libx264", "-t", "3", "-pix_fmt", "yuv420p", "-y", intro_output
], capture_output=True)

print(f"   ✅ Modern intro created: {intro_output}\n")

# Modern Outro Card - Strong CTA with Visual Hierarchy
print("2. Creating modern outro CTA card...")

outro_output = f"/tmp/modern_outro_card_{timestamp}.mp4"

# Create outro with:
# - Bold gradient background
# - Clear visual hierarchy
# - Action-oriented design
subprocess.run([
    "ffmpeg", "-f", "lavfi", "-i", "color=c=#0A2E4D:s=1080x1920:d=6",
    "-vf",
    # Gradient background (professional blue)
    "drawbox=x=0:y=0:w=1080:h=960:color=#0A2E4D@1.0:t=fill,"
    "drawbox=x=0:y=960:w=1080:h=960:color=#1B5E8C@0.95:t=fill,"
    # Accent bars for visual interest
    "drawbox=x=0:y=550:w=1080:h=6:color=#2A9D8F@0.9:t=fill,"
    "drawbox=x=0:y=1300:w=1080:h=6:color=#2A9D8F@0.9:t=fill,"
    # Main CTA Hook - BOLD
    "drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:"
    "text='READY TO':"
    "fontcolor=white:"
    "fontsize=95:"
    "x=(w-text_w)/2:"
    "y=400:"
    "borderw=0,"
    "drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:"
    "text='TRANSFORM?':"
    "fontcolor=#FFD700:"
    "fontsize=110:"
    "x=(w-text_w)/2:"
    "y=500:"
    "borderw=0,"
    # Primary action
    "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:"
    "text='Book Your Free Consultation':"
    "fontcolor=white:"
    "fontsize=65:"
    "x=(w-text_w)/2:"
    "y=700:"
    "borderw=0,"
    # Website - Prominent
    "drawbox=x=240:y=870:w=600:h=120:color=#2A9D8F@0.2:t=fill,"
    "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:"
    "text='LeniLani.com':"
    "fontcolor=#00D9FF:"
    "fontsize=90:"
    "x=(w-text_w)/2:"
    "y=900:"
    "borderw=0,"
    # Phone - Clear
    "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:"
    "text='808-766-1164':"
    "fontcolor=white:"
    "fontsize=70:"
    "x=(w-text_w)/2:"
    "y=1080:"
    "borderw=0,"
    # Urgency - Subtle but effective
    "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:"
    "text='Limited Availability This Month':"
    "fontcolor=#FF6B35:"
    "fontsize=52:"
    "x=(w-text_w)/2:"
    "y=1400:"
    "borderw=0",
    "-c:v", "libx264", "-t", "6", "-pix_fmt", "yuv420p", "-y", outro_output
], capture_output=True)

print(f"   ✅ Modern outro created: {outro_output}\n")

print(f"{'='*80}")
print("✅ MODERN CARDS COMPLETE!")
print(f"{'='*80}\n")
print(f"📁 Intro: {intro_output}")
print(f"📁 Outro: {outro_output}")
print("\nDesign Features:")
print("• Bold, clean typography")
print("• Professional gradient backgrounds")
print("• Clear visual hierarchy")
print("• Mobile-optimized 9:16 format")
print("• Action-oriented CTA")
print("="*80 + "\n")

# Preview intro
subprocess.run(["open", intro_output])
print("Opening intro card preview...")

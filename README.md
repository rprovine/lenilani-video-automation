# Video Generation Tool 🎬

AI-powered viral video generation system using Google Veo 3, Imagen 4, and Claude AI. Automatically creates cinematic 30-second videos for social media platforms (YouTube Shorts, Instagram Reels, TikTok, X/Twitter).

## Features

- **AI Topic Research**: Automatically researches trending topics relevant to Hawaii businesses
- **Cinematic Video Generation**: Creates 3x 8-second clips with Hollywood-style cinematography using Google Veo 3
- **Professional Title Cards**: Generates beautiful title cards with Imagen 4
- **Video Composition**: Merges clips and title cards into cohesive 30-second videos
- **Viral Captions**: AI-generated platform-optimized captions with hashtags
- **Multi-Platform Publishing**: Uploads to YouTube, Instagram, TikTok, and X/Twitter
- **Automated Scheduling**: Daily cron job for automated video generation

## Architecture

```
video-generation-tool/
├── api/
│   └── index.py              # FastAPI application
├── src/
│   ├── config.py             # Configuration and settings
│   ├── services/
│   │   ├── claude_client.py       # Claude AI for prompts & research
│   │   ├── veo_client.py          # Google Veo 3 video generation
│   │   ├── google_image_client.py # Google Imagen 4 image generation
│   │   └── social_media_uploader.py # Social media uploads
│   ├── workflows/
│   │   └── video_generator.py     # Main workflow orchestrator
│   └── utils/
│       └── video_composer.py      # FFmpeg video composition
├── requirements.txt
├── vercel.json               # Vercel deployment config
└── .env.example
```

## Technology Stack

- **AI Models**:
  - Claude Sonnet 4 (topic research, cinematic prompts, captions)
  - Google Veo 3 (video generation)
  - Google Imagen 4 (title card generation)
- **Framework**: FastAPI (Python 3.11+)
- **Video Processing**: FFmpeg
- **Deployment**: Vercel serverless functions
- **Social Media APIs**: YouTube Data API, Instagram Graph API, TikTok API, Twitter API v2

## Setup

### 1. Prerequisites

- Python 3.11+
- FFmpeg (required for video composition)
- Anthropic API key
- Google AI API key with Veo 3 and Imagen 4 access

### 2. Installation

```bash
# Clone the repository
cd video-generation-tool

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (macOS)
brew install ffmpeg

# Install FFmpeg (Ubuntu/Debian)
sudo apt-get install ffmpeg

# Install FFmpeg (Windows)
# Download from https://ffmpeg.org/download.html
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# Required:
# - ANTHROPIC_API_KEY
# - GOOGLE_API_KEY
# - GOOGLE_PROJECT_ID

# Optional (for social media publishing):
# - YouTube credentials
# - Instagram credentials
# - TikTok credentials
# - Twitter credentials
```

### 4. Deployment to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Configure environment variables in Vercel dashboard:
# - ANTHROPIC_API_KEY
# - GOOGLE_API_KEY
# - GOOGLE_PROJECT_ID
# - Social media credentials (optional)
```

## Usage

### API Endpoints

#### Generate Video (Manual)
```bash
POST /generate-video
{
  "topic": "AI for Hawaii Businesses",  # Optional - will research if omitted
  "category": "AI",                     # Optional category focus
  "publish_immediately": true           # Auto-publish to social media
}
```

#### Daily Cron Job
```bash
POST /cron/daily-video
# Automatically runs at 6pm UTC (8am HST) daily
```

#### Health Check
```bash
GET /health
```

### Example Request

```bash
curl -X POST https://your-app.vercel.app/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "topic": null,
    "category": "digital marketing",
    "publish_immediately": true
  }'
```

### Response
```json
{
  "success": true,
  "topic": "AI-Powered Social Media for Hawaii Hotels",
  "final_video_path": "/tmp/final_video_12345.mp4",
  "social_media_urls": {
    "youtube": "https://youtube.com/shorts/abc123",
    "instagram": "https://instagram.com/reel/xyz789",
    "tiktok": "https://tiktok.com/@lenilani/video/456def",
    "twitter": "https://twitter.com/lenilani/status/789ghi"
  },
  "message": "Video generated successfully! Uploaded to 4 platforms"
}
```

## Workflow

1. **Topic Research**: Claude researches 5-10 trending topics with visual appeal
2. **Topic Selection**: AI selects best topic aligned with LeniLani services
3. **Prompt Generation**: Creates cinematic prompts for 3 video clips
4. **Video Generation**: Veo 3 generates 3x 8-second clips in parallel
5. **Title Card**: Imagen 4 creates professional title card
6. **Composition**: FFmpeg merges clips + title card into final video
7. **Caption Generation**: Platform-optimized captions with hashtags
8. **Publishing**: Uploads to YouTube, Instagram, TikTok, X/Twitter

## Video Specifications

- **Duration**: 30 seconds (3x 8-second clips + 3-second title card)
- **Aspect Ratio**: 9:16 (vertical for social media)
- **Frame Rate**: 30 fps
- **Quality**: High (1080x1920)
- **Format**: MP4

## Cinematic Prompting

Videos use Hollywood-style cinematography with:
- Camera movements (dolly, tracking, crane, orbit)
- Lighting details (golden hour, rim lighting, volumetric)
- Camera angles (wide, close-up, over-shoulder)
- Atmospheric elements (lens flares, depth of field)
- Hawaiian/tropical settings
- Emotional storytelling arc

## Social Media Integration

### YouTube Shorts
- OAuth 2.0 authentication
- Auto-categorized as Shorts
- Optimized descriptions and tags

### Instagram Reels
- Instagram Graph API
- Business/Creator account required
- Hashtag optimization

### TikTok
- TikTok for Developers API
- Trending hashtag integration
- Viral caption formatting

### X/Twitter
- API v2 media upload
- Chunked video upload
- Character-optimized captions

## Development

### Running Locally

```bash
# Start development server
uvicorn api.index:app --reload --port 8000

# Test endpoint
curl http://localhost:8000/health
```

### Testing

```bash
# Test video generation locally
python -m pytest tests/

# Manual test
python scripts/test_generation.py
```

## Environment Variables

See `.env.example` for all configuration options.

### Required
- `ANTHROPIC_API_KEY`: Claude AI API key
- `GOOGLE_API_KEY`: Google AI API key (Veo 3 + Imagen 4)
- `GOOGLE_PROJECT_ID`: Google Cloud project ID

### Optional (Social Media)
- YouTube: `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`
- Instagram: `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_ACCOUNT_ID`
- TikTok: `TIKTOK_ACCESS_TOKEN`, `TIKTOK_USER_ID`
- Twitter: `TWITTER_BEARER_TOKEN`, `TWITTER_API_KEY`, etc.

### Application Settings
- `VIDEO_DURATION`: Total video duration (default: 30)
- `CLIP_DURATION`: Individual clip duration (default: 8)
- `NUM_CLIPS`: Number of clips per video (default: 3)
- `CLAUDE_TEMPERATURE`: Creativity level (default: 0.9)

## Cron Schedule

The system automatically generates videos daily at:
- **6pm UTC** = 8am HST (Hawaii Standard Time)

Configure in `vercel.json`:
```json
"crons": [
  {
    "path": "/cron/daily-video",
    "schedule": "0 18 * * *"
  }
]
```

## Troubleshooting

### FFmpeg Not Found
Ensure FFmpeg is installed and available in PATH:
```bash
ffmpeg -version
```

### Video Generation Timeout
Veo 3 may take 5+ minutes per clip. Vercel functions have a 10-minute timeout on Hobby plan, 60 minutes on Pro.

### Social Media Upload Failures
Check credentials and API permissions. Social media uploads require:
- YouTube: OAuth 2.0 with `youtube.upload` scope
- Instagram: Business/Creator account + Graph API access
- TikTok: Developer account + API approval
- Twitter: Elevated API access

## Limitations

- **Veo 3**: Maximum 8 seconds per clip
- **Vercel Free**: 10-second function timeout (use Pro for production)
- **Social Media**: Platform-specific rate limits apply
- **FFmpeg**: Required for video composition (must be installed separately)

## Future Enhancements

- [ ] Add video transitions (crossfades, wipes)
- [ ] Implement actual social media API integrations
- [ ] Add text overlays and captions to video
- [ ] Support custom branding/logos
- [ ] Analytics and performance tracking
- [ ] A/B testing for viral optimization

## License

Proprietary - LeniLani Consulting

## Support

For issues or questions, contact hello@lenilani.com

"""
Main FastAPI application entry point for Vercel deployment.
Handles video generation API endpoints.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime
import logging

# Import our workflows
from src.workflows.video_generator import video_generator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Video Generation Tool API",
    description="AI-powered video generation for social media using Google Veo 3",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class GenerateVideoRequest(BaseModel):
    topic: Optional[str] = None
    category: Optional[str] = None
    publish_immediately: bool = True

class GenerateVideoResponse(BaseModel):
    success: bool
    topic: Optional[str] = None
    final_video_path: Optional[str] = None
    social_media_urls: Optional[dict] = None
    message: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    environment: str

# Health check endpoint
@app.get("/", response_model=HealthResponse)
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify the API is running."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        environment=os.getenv("ENVIRONMENT", "development")
    )

# Generate video endpoint
@app.post("/generate-video", response_model=GenerateVideoResponse)
async def generate_video(request: GenerateVideoRequest):
    """
    Generate a viral video using AI.

    This endpoint:
    1. Researches trending topics (if no topic provided)
    2. Generates cinematic video prompts using Claude AI
    3. Creates 3 video clips using Google Veo 3
    4. Generates title card using Google Imagen 4
    5. Composes final video
    6. Uploads to social media platforms (YouTube, Instagram, TikTok, X)
    """
    try:
        logger.info(f"Starting video generation - Topic: {request.topic}, Category: {request.category}")

        # Run the complete workflow
        result = await video_generator.generate_and_publish(
            topic=request.topic,
            category=request.category,
            publish_immediately=request.publish_immediately
        )

        if result["success"]:
            return GenerateVideoResponse(
                success=True,
                topic=result.get("topic"),
                final_video_path=result.get("final_video_path"),
                social_media_urls=result.get("social_media_urls"),
                message=f"Video generated successfully! Uploaded to {len(result.get('social_media_urls', {}))} platforms"
            )
        else:
            return GenerateVideoResponse(
                success=False,
                message=f"Video generation failed: {', '.join(result.get('errors', ['Unknown error']))}"
            )

    except Exception as e:
        logger.error(f"Error in generate_video endpoint: {e}", exc_info=True)
        return GenerateVideoResponse(
            success=False,
            message=f"Error: {str(e)}"
        )

# Manual trigger endpoint (same as generate-video but with simpler name)
@app.post("/generate-now")
async def generate_now(request: GenerateVideoRequest):
    """Manually trigger video generation."""
    return await generate_video(request)

# Cron endpoint - Daily video generation
@app.post("/cron/daily-video")
async def daily_video_cron():
    """
    Daily video cron job.
    Researches trending topics and generates a viral video for social media.
    """
    try:
        logger.info("=" * 80)
        logger.info("DAILY VIDEO CRON JOB TRIGGERED")
        logger.info("=" * 80)

        # Generate and publish video
        result = await video_generator.generate_and_publish(
            topic=None,  # Will research trending topics
            category=None,  # Will use all categories
            publish_immediately=True
        )

        logger.info("=" * 80)
        logger.info("DAILY VIDEO PUBLISHED SUCCESSFULLY")
        logger.info(f"Topic: {result.get('topic')}")
        logger.info(f"Platforms: {list(result.get('social_media_urls', {}).keys())}")
        logger.info("=" * 80)

        return {
            "success": True,
            "message": "Daily video published successfully",
            "topic": result.get("topic"),
            "platforms": list(result.get("social_media_urls", {}).keys()),
            "urls": result.get("social_media_urls"),
            "timestamp": result.get("timestamp")
        }

    except Exception as e:
        logger.error(f"Error in daily video cron job: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate daily video"
        }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "message": "The requested endpoint does not exist"
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred"
    }

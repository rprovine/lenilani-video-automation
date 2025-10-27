"""
Configuration settings for the video generation system.
Loads and validates all environment variables.
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Anthropic API
    anthropic_api_key: str

    # Google AI APIs (Veo 3 & Imagen 4)
    google_api_key: str
    google_project_id: str = "YOUR_PROJECT_ID"
    google_region: str = "us-central1"

    # ElevenLabs API (Voiceover)
    elevenlabs_api_key: str

    # Suno AI API (Music Generation)
    suno_api_key: Optional[str] = None
    suno_cookie: Optional[str] = None  # Alternative to API key
    suno_base_url: str = "http://localhost:3000"  # Local suno-api server

    # Social Media APIs
    youtube_client_id: Optional[str] = None
    youtube_client_secret: Optional[str] = None
    youtube_refresh_token: Optional[str] = None

    instagram_access_token: Optional[str] = None
    instagram_account_id: Optional[str] = None

    tiktok_access_token: Optional[str] = None
    tiktok_user_id: Optional[str] = None

    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_secret: Optional[str] = None
    twitter_bearer_token: Optional[str] = None

    # HubSpot API
    hubspot_access_token: Optional[str] = None
    hubspot_portal_id: Optional[str] = None

    # Application Settings
    environment: str = "development"

    # Video Settings
    video_duration: int = 30  # Total video duration in seconds
    clip_duration: int = 8    # Individual clip duration
    num_clips: int = 3        # Number of clips per video

    # AI Settings
    claude_model: str = "claude-sonnet-4-5-20250929"
    claude_temperature: float = 0.9  # High creativity for video prompts
    claude_max_tokens: int = 4000

    # Company Info
    company_name: str = "LeniLani Consulting"
    company_website: str = "https://www.lenilani.com"
    company_tagline: str = "AI-Powered Business Solutions for Hawaii"
    company_phone: str = "(808) 555-0123"  # Update with real number
    company_email: str = "hello@lenilani.com"

    @field_validator('*', mode='before')
    @classmethod
    def strip_strings(cls, v):
        """Strip whitespace from all string values."""
        if isinstance(v, str):
            return v.strip()
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

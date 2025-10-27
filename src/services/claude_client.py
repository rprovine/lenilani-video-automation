"""
Claude AI client service using Anthropic API.
Handles all AI-powered content generation.
"""

from anthropic import Anthropic
from typing import Dict, Any, Optional, List
import logging
import json
import re
from ..config import settings

logger = logging.getLogger(__name__)


def extract_json_from_response(response_text: str) -> Any:
    """
    Extract JSON from Claude response, handling markdown code blocks and escape sequences.

    Args:
        response_text: Raw response from Claude

    Returns:
        Parsed JSON object
    """
    import ast

    # Try to find JSON in markdown code blocks
    json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1).strip()
    else:
        # If no code block, try to find JSON object/array
        json_match = re.search(r'(\{.*\}|\[.*\])', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
        else:
            # Last resort: use the whole response
            json_str = response_text.strip()

    # Try multiple parsing strategies
    # 1. Direct json.loads
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning(f"Direct JSON parsing failed: {e}")

    # 2. Try with strict=False to be more lenient
    try:
        return json.loads(json_str, strict=False)
    except json.JSONDecodeError as e:
        logger.warning(f"Lenient JSON parsing failed: {e}")

    # 3. Try using ast.literal_eval as last resort (converts Python dict syntax)
    try:
        return ast.literal_eval(json_str)
    except (ValueError, SyntaxError) as e:
        logger.error(f"All JSON parsing strategies failed: {e}")
        logger.error(f"Problematic JSON string (first 500 chars): {json_str[:500]}")
        raise ValueError(f"Could not parse JSON from Claude response: {str(e)}")


class ClaudeService:
    """Service for interacting with Claude AI for video generation."""

    def __init__(self):
        """Initialize Claude client."""
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.claude_model
        self.temperature = settings.claude_temperature
        self.max_tokens = settings.claude_max_tokens

    async def generate_content(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate content using Claude.

        Args:
            system_prompt: System instructions for Claude
            user_prompt: User message/prompt
            temperature: Temperature override (default from settings)
            max_tokens: Max tokens override (default from settings)

        Returns:
            Generated text content
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )

            # Extract text from response
            content = response.content[0].text if response.content else ""

            logger.info(f"Generated content ({len(content)} chars)")
            return content
        except Exception as e:
            logger.error(f"Error generating content with Claude: {e}")
            raise

    async def research_trending_topics(self, focus_area: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Research current trending topics suitable for viral video content.

        Args:
            focus_area: Optional focus area (e.g., "AI", "digital marketing")

        Returns:
            List of trending topics with video potential
        """
        try:
            system_prompt = """You are a viral video content researcher and strategist. Your task is to identify
current trending topics in technology and business that would make compelling, viral-worthy short-form video
content (30 seconds). Focus on topics that:
1. Are visually interesting and cinematic
2. Have emotional appeal or wow-factor
3. Are relevant for Hawaii businesses
4. Can be explained quickly with strong storytelling
5. Relate to practical business applications"""

            focus_text = f" with a focus on {focus_area}" if focus_area else ""
            user_prompt = f"""Research and list 5-10 trending topics{focus_text} that would make excellent
30-second viral video content for Hawaii businesses. For each topic, provide:
1. Topic title
2. Brief description (2-3 sentences)
3. Why it's visually compelling for video
4. Business relevance to Hawaii

Return as a JSON array of objects with keys: title, description, visual_appeal, hawaii_relevance"""

            response_text = await self.generate_content(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )

            # Parse JSON response
            topics = extract_json_from_response(response_text)

            logger.info(f"Researched {len(topics)} trending video topics")
            return topics
        except Exception as e:
            logger.error(f"Error researching trending topics: {e}")
            raise

    async def select_video_topic(
        self,
        topics: List[Dict[str, str]],
        services: List[str]
    ) -> Dict[str, Any]:
        """
        Select the best topic for video content aligned with LeniLani services.

        Args:
            topics: List of trending topics
            services: List of LeniLani services

        Returns:
            Dict with selected topic and reasoning
        """
        try:
            topics_text = "\n\n".join([
                f"{i+1}. {topic['title']}\n   {topic['description']}\n   Visual Appeal: {topic.get('visual_appeal', 'N/A')}\n   Hawaii Relevance: {topic.get('hawaii_relevance', 'N/A')}"
                for i, topic in enumerate(topics)
            ])

            services_text = "\n".join([f"- {service}" for service in services])

            system_prompt = """You are a viral video content strategist for LeniLani Consulting, a Hawaii-based
technology consulting firm. Select the most compelling video topic that:
1. Has strong visual storytelling potential
2. Aligns with LeniLani's services
3. Will resonate with Hawaii businesses
4. Can create emotional impact in 30 seconds"""

            user_prompt = f"""Given these LeniLani services:
{services_text}

And these trending topics:
{topics_text}

Select the best topic for a 30-second viral video and explain:
1. Which service it aligns with
2. Why it's perfect for video storytelling
3. Key emotional beats to hit
4. CTA (Call to Action) to include

Return as JSON with keys: selected_topic, service_alignment, storytelling_approach, emotional_beats, cta"""

            response_text = await self.generate_content(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )

            # Parse JSON response
            selection = extract_json_from_response(response_text)

            logger.info(f"Selected video topic: {selection.get('selected_topic', 'Unknown')}")
            return selection
        except Exception as e:
            logger.error(f"Error selecting video topic: {e}")
            raise

    async def generate_video_prompts(
        self,
        topic: str,
        service_focus: str,
        storytelling_approach: str,
        emotional_beats: List[str],
        cta: str
    ) -> Dict[str, Any]:
        """
        Generate cinematic, Hollywood-style prompts for 3 video clips that tell a cohesive story.

        Args:
            topic: The video topic
            service_focus: LeniLani service to focus on
            storytelling_approach: How to tell the story
            emotional_beats: Emotional moments to hit
            cta: Call to action

        Returns:
            Dict with 3 clip prompts, title card text, and viral captions
        """
        try:
            beats_text = "\n".join([f"- {beat}" for beat in emotional_beats])

            system_prompt = f"""You are a Hollywood cinematographer and viral video creator specializing in
cinematic short-form content. Create HIGHLY DETAILED, CINEMATIC prompts for Google Veo 3 video generation.

CRITICAL REQUIREMENTS FOR CINEMATIC QUALITY:
- Every prompt must specify camera movements (dolly, tracking, crane, orbit, etc.)
- Include lighting details (golden hour, rim lighting, volumetric, etc.)
- Specify exact camera angles and framing (wide establishing, close-up, over-shoulder, etc.)
- Add atmospheric elements (lens flares, depth of field, motion blur, etc.)
- Use Hollywood terminology and cinematic language
- Each shot should build tension and emotional engagement
- Think in terms of visual storytelling, not just description

For Hawaii/tropical settings:
- Leverage natural beauty (ocean, palm trees, mountains, beaches)
- Use local business settings authentically
- Incorporate island lifestyle and culture
- Golden hour lighting over the Pacific
- Vibrant tropical colors

STORY STRUCTURE for 3 clips (24 seconds total):
Clip 1 (8 sec): THE HOOK - Establish the problem/opportunity with stunning visuals
Clip 2 (8 sec): THE SOLUTION - Show the transformation/possibility in action
Clip 3 (8 sec): THE PAYOFF - Deliver emotional impact and hint at CTA

Format: 9:16 vertical video for social media (Instagram Reels, TikTok, YouTube Shorts)

Company: {settings.company_name}
Website: {settings.company_website}
Tagline: {settings.company_tagline}"""

            user_prompt = f"""Create a 3-clip cinematic video about: {topic}

Service Focus: {service_focus}
Storytelling Approach: {storytelling_approach}
Emotional Beats to Hit:
{beats_text}
Call to Action: {cta}

PROVIDE:
1. Three detailed cinematic prompts (one for each 8-second clip)
2. Title card design and text (company info, CTA, visual style)
3. Viral captions for each platform (Instagram, TikTok, YouTube, X/Twitter)

Each video prompt must include:
- Opening camera setup and movement
- Subject/action description with emotional context
- Lighting and atmosphere details
- Color grading mood
- Transition suggestion to next clip
- Specific Hawaiian/tropical elements if relevant

EXAMPLE OF GOOD CINEMATIC PROMPT:
"Opening with a dramatic crane shot descending from above Diamond Head crater at golden hour, warm amber
sunlight creating lens flares, transitioning to a smooth tracking shot following a Hawaiian restaurant owner
walking through their modern open-air dining space, natural rim lighting from setting sun, shallow depth of
field focusing on their confident expression, vibrant tropical plants and ocean view blurred in background,
color grade: warm tones with teal shadows, ending with a slow push-in as they interact with a sleek AI-powered
ordering tablet on polished koa wood table, professional cinema camera quality, 30fps"

BAD EXAMPLE (too generic):
"Person using technology in Hawaii"

Return as JSON with keys:
- clip_1_prompt (detailed cinematic prompt)
- clip_2_prompt (detailed cinematic prompt)
- clip_3_prompt (detailed cinematic prompt)
- title_card_design (visual description and text content with company info: {settings.company_name}, {settings.company_website}, {settings.company_phone}, {settings.company_email})
- captions (object with keys: instagram, tiktok, youtube, twitter - each optimized for viral potential with hooks, hashtags, emojis)"""

            response_text = await self.generate_content(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.9,  # High creativity for cinematic prompts
                max_tokens=6000
            )

            # Parse JSON response
            prompts = extract_json_from_response(response_text)
            logger.info("Generated cinematic video prompts for 3 clips")
            return prompts
        except Exception as e:
            logger.error(f"Error generating video prompts: {e}")
            raise

    async def generate_title_card_prompt(self, topic: str, cta: str) -> str:
        """
        Generate an Imagen prompt for the title card with company info and CTA.

        Args:
            topic: The video topic
            cta: Call to action text

        Returns:
            Image generation prompt for the title card
        """
        try:
            system_prompt = """You are a professional graphic designer specializing in social media title cards.
Create detailed prompts for Google Imagen 4 to generate beautiful, professional title cards for video endings."""

            user_prompt = f"""Create a title card image prompt for a video about: {topic}

The title card should include space for:
- Company Name: {settings.company_name}
- Tagline: {settings.company_tagline}
- Website: {settings.company_website}
- Call to Action: {cta}

Design requirements:
- Professional, modern, clean design
- Hawaiian/tropical aesthetic (ocean colors, palm motifs, island vibes)
- 9:16 aspect ratio for vertical video
- Clear hierarchy with readable text areas
- Vibrant but professional color palette
- Space for overlay text (we'll add text in post-production)

Return ONLY the detailed image generation prompt (no explanations, just the prompt text)."""

            prompt = await self.generate_content(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.8
            )

            logger.info("Generated title card prompt")
            return prompt.strip()
        except Exception as e:
            logger.error(f"Error generating title card prompt: {e}")
            raise


# Global instance
claude_service = ClaudeService()

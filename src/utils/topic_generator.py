"""
Generate diverse video topics for variety.
Each video follows: PROBLEM → SOLUTION → CTA
"""
import random
from typing import Dict, List

class TopicGenerator:
    """Generates diverse business scenarios for video content."""

    # Different business types
    BUSINESS_TYPES = [
        "restaurant",
        "retail store",
        "medical practice",
        "real estate agency",
        "hotel",
        "dental office",
        "law firm",
        "spa and salon",
        "auto repair shop",
        "construction company",
        "accounting firm",
        "gym and fitness center",
        "coffee shop",
        "property management company"
    ]

    # Different business problems
    PROBLEMS = [
        {
            "title": "DROWNING IN PAPERWORK",
            "scenario": "overwhelmed by manual data entry and paper documents piling up everywhere",
            "pain": "spending hours on administrative tasks instead of serving customers"
        },
        {
            "title": "LOSING CUSTOMERS",
            "scenario": "struggling to respond to customer inquiries fast enough",
            "pain": "customers leaving negative reviews about slow response times"
        },
        {
            "title": "SCHEDULING NIGHTMARE",
            "scenario": "juggling appointments and double-bookings constantly",
            "pain": "losing revenue from scheduling conflicts and no-shows"
        },
        {
            "title": "INVENTORY CHAOS",
            "scenario": "running out of stock or over-ordering products",
            "pain": "wasting money on excess inventory or losing sales from stockouts"
        },
        {
            "title": "NO ONLINE PRESENCE",
            "scenario": "competitors dominating online while you're invisible",
            "pain": "potential customers can't find you and going to competitors instead"
        },
        {
            "title": "OVERWHELMED BY CALLS",
            "scenario": "phone ringing non-stop with the same questions",
            "pain": "staff exhausted answering repetitive calls instead of important work"
        },
        {
            "title": "MANUAL INVOICING",
            "scenario": "creating invoices by hand and chasing payments",
            "pain": "cash flow problems from late payments and billing errors"
        },
        {
            "title": "ZERO MARKETING",
            "scenario": "no time or knowledge to market your business effectively",
            "pain": "relying only on word-of-mouth while competitors steal market share"
        },
        {
            "title": "DATA DISASTER",
            "scenario": "important business data scattered across spreadsheets and notebooks",
            "pain": "making decisions blindly without real insights into your business"
        },
        {
            "title": "HIRING HEADACHES",
            "scenario": "spending weeks screening unqualified candidates",
            "pain": "positions staying empty while your team burns out from overwork"
        }
    ]

    # AI Solutions
    SOLUTIONS = [
        "AI-powered automation handling repetitive tasks instantly",
        "Intelligent chatbots responding to customers 24/7",
        "Smart scheduling system preventing conflicts automatically",
        "Predictive inventory management optimizing stock levels",
        "AI-generated content boosting your online visibility",
        "Virtual assistant answering common questions automatically",
        "Automated billing and payment reminders",
        "AI marketing campaigns targeting ideal customers",
        "Real-time analytics dashboard showing key business metrics",
        "AI candidate screening finding perfect hires faster"
    ]

    # Call to Action variations
    CTAS = [
        {
            "hook": "READY FOR CHANGE?",
            "action": "Book Your Free AI Consultation",
            "urgency": "Limited Spots Available This Month"
        },
        {
            "hook": "TRANSFORM YOUR BUSINESS",
            "action": "Get Your Custom AI Strategy",
            "urgency": "Free Analysis - No Commitment"
        },
        {
            "hook": "DON'T FALL BEHIND",
            "action": "Start Your AI Journey Today",
            "urgency": "Your Competitors Already Are"
        },
        {
            "hook": "IMAGINE THE FREEDOM",
            "action": "Schedule Your AI Demo Now",
            "urgency": "See Results In 30 Days"
        },
        {
            "hook": "STOP STRUGGLING",
            "action": "Let AI Do The Heavy Lifting",
            "urgency": "Free Trial - Risk Free"
        }
    ]

    def generate_video_concept(self) -> Dict[str, any]:
        """Generate a complete video concept with variety."""

        # Pick random elements
        business_type = random.choice(self.BUSINESS_TYPES)
        problem = random.choice(self.PROBLEMS)
        solution = random.choice(self.SOLUTIONS)
        cta = random.choice(self.CTAS)

        # Location variety for Hawaii
        locations = ["Honolulu", "Maui", "Kauai", "Big Island", "Oahu"]
        location = random.choice(locations)

        return {
            "business_type": business_type,
            "location": location,
            "problem": problem,
            "solution": solution,
            "cta": cta,

            # Video prompts following Problem → Solution → CTA structure
            "clip_1_prompt": f"""Cinematic widescreen video (16:9 landscape, 1080p): A stressed {business_type} owner in {location}, Hawaii {problem['scenario']}. Camera slowly zooms in on their frustrated, exhausted expression. Their workspace is chaotic and disorganized. Warm natural lighting. Professional office setting with tropical plants visible. High-quality commercial cinematography, shallow depth of field, 8 seconds. Film grain texture, professional color grading.""",

            "clip_2_prompt": f"""Cinematic widescreen video (16:9 landscape, 1080p): Same {business_type} owner in {location} now discovering {solution}. Their face lights up with hope and excitement as they see the solution on their laptop screen showing LeniLani Consulting branding. Modern clean office with organized workspace. Camera pans from concerned to relieved expression. Bright, hopeful lighting with ocean view through window. Professional commercial quality, 8 seconds. Film grain texture, professional color grading.""",

            "clip_3_prompt": f"""Cinematic widescreen video (16:9 landscape, 1080p): {business_type} owner in {location} now thriving and confident. They're working efficiently with AI dashboard visible on screen, smiling and relaxed. Happy customers visible in background. Clean, modern office space. Warm golden hour lighting. Camera shows before/after transformation moment. Professional success story aesthetic, vibrant colors, 8 seconds. Film grain texture, professional color grading.""",

            # Text overlays
            "clip_1_text": problem['title'],
            "clip_2_text": "AI POWERED SOLUTION",
            "clip_3_text": f"{cta['hook']}",

            # CTA details for outro
            "cta_main": cta['action'],
            "cta_urgency": cta['urgency'],

            # Voiceover script
            "voiceover_script": f"""
            Are you a {business_type} owner in Hawaii {problem['pain']}?

            You're not alone. But there's a better way.

            {solution} - that's what LeniLani Consulting brings to Hawaii businesses like yours.

            We've helped dozens of local businesses automate their operations, save thousands of hours, and dramatically increase revenue.

            {cta['action']}. Call 808-766-1164 or visit LeniLani.com.

            {cta['urgency']}. Don't let your competitors leave you behind.
            """.strip()
        }

    def generate_batch(self, count: int = 5) -> List[Dict]:
        """Generate multiple unique video concepts."""
        concepts = []
        used_combinations = set()

        while len(concepts) < count:
            concept = self.generate_video_concept()

            # Ensure uniqueness
            key = (concept['business_type'], concept['problem']['title'])
            if key not in used_combinations:
                used_combinations.add(key)
                concepts.append(concept)

        return concepts


# Global instance
topic_generator = TopicGenerator()

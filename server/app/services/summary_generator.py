"""
Summary generation service using OpenAI GPT models.
"""

import logging
from openai import OpenAI
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SummaryGenerator:
    """Service to generate summaries from transcripts."""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model_name = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")

    def generate_summary(self, transcript: str) -> str:
        """Generate an approximately 300-character English summary using GPT.
        If the API call fails or input is empty, return the input as-is.
        """
        text = (transcript or "").strip()
        if not text:
            return ""

        # Keep reasonable input size to avoid excessive token usage
        if len(text) > 4000:
            text = text[:4000]
        
        logger.info(f"Summary generation started. Text: {text}")

        system_prompt = (
            "You write clear, skimmable English summaries.\n"
            "Output Markdown with the following sections only:\n"
            "1) **Summary** (1–2 sentences)\n"
            "2) **Key Details** (3–6 bullets, full phrases)\n"
            "3) **Takeaways** (2–3 bullets)\n"
            "Rules:\n"
            f"- Total length: 300-350 words.\n"
        )

        user_prompt = (
            "Summarize the following:\n\n"
            f"{text}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=2000,
            )

            logger.info(f"API Response: {response}")
            logger.info(f"Response choices: {response.choices}")
            logger.info(f"Response usage: {response.usage}")
            
            completion = response.choices[0].message.content if response.choices else None
            logger.info(f"Summary generation completed. Completion: {completion}")
            if completion:
                return completion.strip()
        except Exception as e:
            logger.warning(f"Summary generation via GPT failed: {e}")

        # Fallback: return original transcript (no truncation)
        return (transcript or "").strip()



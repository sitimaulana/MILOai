"""
MILO AI Backend - Fast English to Indonesian Translation Helper
Translates conversational tutor messages into natural Indonesian for the learning safety net.
"""

import logging
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)

TRANSLATE_SYSTEM_PROMPT = """\
You are an expert English-to-Indonesian translator for an English speaking practice app.
Translate the following English message spoken by an AI English tutor into natural, polite, and conversational Indonesian.
Maintain the friendly, supportive tutor persona.
Output ONLY the clean Indonesian translation without any explanations, quotes, or markdown formatting.
"""

class FastTranslator:
    """Async translator using the configured LLM provider."""

    def __init__(self) -> None:
        if settings.ai_provider == "local":
            self._client = AsyncOpenAI(
                api_key="ollama",
                base_url=settings.ollama_base_url,
            )
        elif settings.ai_provider == "bifrost":
            self._client = AsyncOpenAI(
                api_key=settings.bifrost_api_key or "bk-milo-token-gateway",
                base_url=settings.bifrost_base_url,
                default_headers={
                    "X-Bifrost-App": "MILO-AI-Backend",
                },
            )
            self._model = settings.bifrost_model
        elif settings.ai_provider == "openrouter":
            self._client = AsyncOpenAI(
                api_key=settings.openrouter_api_key or "missing_key",
                base_url=settings.openrouter_base_url,
                default_headers={
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "MILO AI English Tutor",
                },
            )
            self._model = settings.openrouter_model
        else:
            self._client = AsyncOpenAI(api_key=settings.openai_api_key)
            self._model = settings.llm_model

    async def translate(self, text: str) -> str:
        """Translate English text to natural Indonesian."""
        if not text or not text.strip():
            return ""

        extra_kwargs = {}
        if settings.ai_provider == "openrouter":
            extra_kwargs["extra_body"] = {
                "reasoning": {"effort": "none"},
                "models": settings.openrouter_model_list,
                "route": "fallback",
            }

        try:
            completion = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": TRANSLATE_SYSTEM_PROMPT},
                    {"role": "user", "content": text.strip()}
                ],
                temperature=0.3,
                max_tokens=256,
                **extra_kwargs,
            )
            message = completion.choices[0].message
            translated = (message.content or getattr(message, "reasoning", "") or "").strip()
            # Clean up accidental surrounding quotes if any
            if translated.startswith('"') and translated.endswith('"'):
                translated = translated[1:-1].strip()
            return translated
        except Exception as e:
            logger.warning(f"Translation failed: {e}")
            return ""

# Global singleton translator instance
fast_translator = FastTranslator()

async def translate_to_indonesian(text: str) -> str:
    """Helper function to translate tutor speech to Indonesian."""
    return await fast_translator.translate(text)

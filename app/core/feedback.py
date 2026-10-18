"""
MILO AI Backend - Language Feedback Engine

Analyzes user utterances for:
  - Grammar errors (subject-verb agreement, tense, articles, prepositions)
  - Vocabulary suggestions (B1 → B2 upgrades)
  - Fluency score (sentence complexity and naturalness)

Uses GPT-4o Mini with JSON structured output for consistent, parseable responses.

Usage:
    from app.core.feedback import analyze_utterance, FeedbackResult

    result = await analyze_utterance(
        user_text="Yesterday I go to the store and buyed some foods.",
        cefr_level="B1",
    )
    print(result.grammar_score)
    print(result.corrections)
"""

import json
import logging
from dataclasses import dataclass, field

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

# ─── Feedback Prompt ──────────────────────────────────────────────────────────

FEEDBACK_SYSTEM_PROMPT = """\
You are an expert English language teacher specialized in CEFR {cefr_level} assessment.
Your task is to analyze a student's English utterance and provide structured feedback focusing on corrections and practical tips across Grammar, Vocabulary, and Fluency.

Respond ONLY with a valid JSON object matching this exact schema:

{{
  "grammar_score": <number 0-100>,
  "vocabulary_score": <number 0-100>,
  "fluency_score": <number 0-100>,
  "corrections": [
    {{
      "original": "<exact phrase with error or improvement opportunity>",
      "corrected": "<corrected or better phrase>",
      "explanation": "<brief, friendly explanation>",
      "error_type": "<grammar|vocabulary|fluency>"
    }}
  ],
  "grammar_tip": "<one specific, actionable tip to improve grammar accuracy for this utterance or topic>",
  "vocabulary_tip": "<one specific tip to use richer {next_level} vocabulary or replace repetitive words>",
  "fluency_tip": "<one specific tip to improve natural flow, linking phrases, or conversational confidence>",
  "positive_note": "<1-2 sentences of genuine encouragement about what was done well>",
  "tip": "<main summary tip>"
}}

Scoring guidelines:
- grammar_score: 100 = perfect grammar. Deduct 10–20 per significant error.
- vocabulary_score: 100 = varied, level-appropriate B1/B2 vocabulary.
- fluency_score: 100 = natural, flowing English and sentence connectors.

Rules:
- Categorize each correction strictly as 'grammar', 'vocabulary', or 'fluency'.
- Keep explanations simple, positive, and encouraging (learner-friendly).
- Always provide actionable tips for grammar_tip, vocabulary_tip, and fluency_tip even if the user made no major mistakes.
- If there are no mistakes, corrections can be an empty array [].
"""

FEEDBACK_USER_PROMPT = """\
Analyze this student utterance:
---
{user_text}
---
"""


@dataclass
class CorrectionItem:
    original: str
    corrected: str
    explanation: str
    error_type: str


@dataclass
class FeedbackResult:
    grammar_score: float
    vocabulary_score: float
    fluency_score: float
    corrections: list[CorrectionItem] = field(default_factory=list)
    positive_note: str = ""
    tip: str = ""
    grammar_tip: str = ""
    vocabulary_tip: str = ""
    fluency_tip: str = ""

    @property
    def overall_score(self) -> float:
        """Weighted average: grammar 40%, vocabulary 30%, fluency 30%."""
        return (
            self.grammar_score * 0.4
            + self.vocabulary_score * 0.3
            + self.fluency_score * 0.3
        )


_LEVEL_PROGRESSION = {"A1": "A2", "A2": "B1", "B1": "B2", "B2": "C1", "C1": "C2", "C2": "C2"}


class FeedbackEngine:
    """Language feedback analyzer using GPT-4o Mini with JSON mode."""

    def __init__(self) -> None:
        if settings.ai_provider == "local":
            self._client = AsyncOpenAI(
                api_key="ollama",
                base_url=settings.ollama_base_url,
            )
            self._model = settings.local_llm_model
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

    async def analyze(
        self,
        user_text: str,
        cefr_level: str = "B1",
    ) -> FeedbackResult:
        """
        Analyze a user's utterance and return structured language feedback.

        Args:
            user_text: The user's spoken/typed English text.
            cefr_level: Target CEFR level for evaluation context.

        Returns:
            FeedbackResult with scores and corrections.
        """
        if not user_text or not user_text.strip():
            return FeedbackResult(
                grammar_score=0.0,
                vocabulary_score=0.0,
                fluency_score=0.0,
                positive_note="No text provided.",
                tip="Try speaking a complete sentence!",
            )

        next_level = _LEVEL_PROGRESSION.get(cefr_level, "C1")

        system_prompt = FEEDBACK_SYSTEM_PROMPT.format(
            cefr_level=cefr_level,
            next_level=next_level,
        )
        user_prompt = FEEDBACK_USER_PROMPT.format(user_text=user_text.strip())

        extra_kwargs = {}
        if settings.ai_provider == "openrouter":
            extra_kwargs["extra_body"] = {
                "reasoning": {"effort": "none"},
                "models": settings.openrouter_model_list,
                "route": "fallback",
            }

        try:
            try:
                completion = await self._client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.2,  # Low temperature for consistent, accurate feedback
                    max_tokens=800,
                    response_format={"type": "json_object"},  # Force JSON output
                    **extra_kwargs,
                )
            except Exception as json_err:
                # If model doesn't support response_format={"type": "json_object"}
                if "response_format" in str(json_err).lower() or "schema" in str(json_err).lower():
                    logger.warning("response_format parameter not supported by model; retrying without it...")
                    completion = await self._client.chat.completions.create(
                        model=self._model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        temperature=0.2,
                        max_tokens=800,
                        **extra_kwargs,
                    )
                else:
                    raise
        except Exception as e:
            logger.error(f"Feedback engine API error: {e}")
            return self._fallback_result()

        raw_content = completion.choices[0].message.content or "{}"
        clean_content = raw_content.strip()
        if clean_content.startswith("```json"):
            clean_content = clean_content[7:]
        elif clean_content.startswith("```"):
            clean_content = clean_content[3:]
        if clean_content.endswith("```"):
            clean_content = clean_content[:-3]
        clean_content = clean_content.strip()

        try:
            data = json.loads(clean_content)
            return self._parse_result(data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback regex/slice for { ... } if markdown contained chatter
            start = clean_content.find("{")
            end = clean_content.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    data = json.loads(clean_content[start : end + 1])
                    return self._parse_result(data)
                except Exception:
                    pass
            logger.error(f"Failed to parse feedback JSON: {e}\nRaw: {raw_content[:200]}")
            return self._fallback_result()

    def _parse_result(self, data: dict) -> FeedbackResult:
        """Parse the raw JSON dict from GPT into a FeedbackResult."""
        corrections = [
            CorrectionItem(
                original=c.get("original", ""),
                corrected=c.get("corrected", ""),
                explanation=c.get("explanation", ""),
                error_type=c.get("error_type", "grammar"),
            )
            for c in data.get("corrections", [])
            if c.get("original") and c.get("corrected")
        ]

        return FeedbackResult(
            grammar_score=float(data.get("grammar_score", 80.0)),
            vocabulary_score=float(data.get("vocabulary_score", 80.0)),
            fluency_score=float(data.get("fluency_score", 80.0)),
            corrections=corrections,
            positive_note=data.get("positive_note", "Good effort!"),
            tip=data.get("tip", "Keep practicing!"),
            grammar_tip=data.get("grammar_tip", "Pay attention to tenses and subject-verb consistency."),
            vocabulary_tip=data.get("vocabulary_tip", "Try incorporating varied descriptive adjectives and synonyms."),
            fluency_tip=data.get("fluency_tip", "Use linking words to smoothly bridge your thoughts."),
        )

    def _fallback_result(self) -> FeedbackResult:
        """Return a safe fallback when the API call fails."""
        return FeedbackResult(
            grammar_score=75.0,
            vocabulary_score=75.0,
            fluency_score=75.0,
            corrections=[],
            positive_note="Great effort! Keep practicing.",
            tip="Focus on speaking clearly and connecting your ideas.",
            grammar_tip="Pay attention to subject-verb agreement and proper verb forms.",
            vocabulary_tip="Try exploring synonyms to avoid repeating common words.",
            fluency_tip="Use natural conversational transitions to keep your answers flowing.",
        )


# Global singleton
feedback_engine = FeedbackEngine()


async def analyze_utterance(
    user_text: str,
    cefr_level: str = "B1",
) -> FeedbackResult:
    """High-level feedback analysis helper used by the pipeline."""
    return await feedback_engine.analyze(user_text, cefr_level)

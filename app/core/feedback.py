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
Your task is to analyze a student's English utterance and provide structured, accurate, and encouraging feedback across Grammar, Vocabulary, and Fluency.

## Important Evaluation Rules:
1. DO NOT INVENT MISTAKES (NO FALSE POSITIVES):
   - If the student's sentence is grammatically correct and natural, DO NOT change it just for stylistic preference. Leave "corrections": [] and award 90-100 scores!
   - In spoken English, short conversational answers (e.g., "Yes, I have.", "I think so.") are completely natural and correct. Do not penalize them for being short.
2. ACCURATE ERROR CATEGORIZATION:
   - 'grammar': True grammatical mistakes (e.g., wrong tense, subject-verb disagreement like 'she go', missing auxiliary, incorrect preposition like 'arrive at/in', singular/plural mismatch).
   - 'vocabulary': Using the wrong word meaning or obvious direct translations (e.g., 'join with us' -> 'join us', 'borrow' vs 'lend').
   - 'fluency': Unnatural phrasing or awkward spoken word order.
3. CONSTRUCTIVE & FRIENDLY:
   - Always encourage the learner. Keep explanations simple, positive, and clear (1 sentence).

## Few-Shot Reference Examples:

Example 1 — Utterance with Grammar Errors:
Student: "Yesterday I go to market and buyed many food."
JSON:
{{
  "grammar_score": 65,
  "vocabulary_score": 75,
  "fluency_score": 70,
  "corrections": [
    {{
      "original": "I go to market",
      "corrected": "I went to the market",
      "explanation": "Use past tense 'went' for past events, and remember the article 'the'.",
      "error_type": "grammar"
    }},
    {{
      "original": "buyed many food",
      "corrected": "bought a lot of food",
      "explanation": "'Bought' is the irregular past tense of buy, and 'food' is uncountable so use 'a lot of' instead of 'many'.",
      "error_type": "grammar"
    }}
  ],
  "grammar_tip": "Review irregular past tense verbs like go -> went and buy -> bought.",
  "vocabulary_tip": "Use quantifiers like 'a variety of groceries' to sound more natural.",
  "fluency_tip": "Try connecting your thoughts with time markers like 'In the morning, I went...'.",
  "positive_note": "Great job sharing what you did yesterday! Your message was very clear.",
  "tip": "Focus on irregular past tense forms for past events."
}}

Example 2 — Well-formed, Correct Utterance (NO false corrections):
Student: "I really enjoy solving complex problems because it challenges my analytical skills."
JSON:
{{
  "grammar_score": 98,
  "vocabulary_score": 95,
  "fluency_score": 95,
  "corrections": [],
  "grammar_tip": "Your sentence structure and subject-verb agreement are spot on!",
  "vocabulary_tip": "You can try {next_level} synonyms like 'tackling intricate problems' to further enrich your language.",
  "fluency_tip": "Excellent use of 'because' to smoothly connect your reasoning.",
  "positive_note": "Outstanding response! Your grammar is accurate and your vocabulary is very professional.",
  "tip": "Keep up this high standard of articulate speaking!"
}}

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
                "reasoning": {"max_tokens": 0},
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
                    max_tokens=450,
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
                        max_tokens=450,
                        **extra_kwargs,
                    )
                else:
                    raise
        except Exception as e:
            logger.error(f"Feedback engine API error: {e}")
            if settings.ai_provider == "openrouter" and self._model != "openrouter/free":
                try:
                    logger.info("Attempting feedback fallback to 'openrouter/free'...")
                    completion = await self._client.chat.completions.create(
                        model="openrouter/free",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        temperature=0.2,
                        max_tokens=450,
                        extra_body={"reasoning": {"max_tokens": 0}},
                    )
                except Exception:
                    return self._fallback_result()
            else:
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

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
from typing import Optional

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

# ─── Feedback Prompt ──────────────────────────────────────────────────────────

FEEDBACK_SYSTEM_PROMPT = """\
You are an expert English language examiner and tutor specialized in CEFR {cefr_level} assessment.
Your task is to analyze a student's English utterance and provide structured, accurate, and encouraging feedback across Grammar, Vocabulary, and Fluency.

## CRITICAL RULES FOR ZERO FALSE POSITIVES:
1. ONLY FLAG REAL ERRORS:
   - A mistake MUST be an objective error in English grammar, word choice, or phrasing (e.g. "he go", "I buyed", "I am agree", "I have 20 years old", "she don't know").
   - If the sentence is grammatically correct and natural spoken English, "corrections" MUST be strictly [] (empty array) and scores MUST be 90-100!
   - Conversational, casual, or short responses (e.g. "I'm good, thanks", "I want to practice speaking", "Yes, I agree with you", "At a software company", "I like watching movies") are 100% correct. DO NOT nitpick, rephrase, or rewrite them!
   - NEVER suggest corrections just for style, fancier synonyms, or formal preferences. Put enrichment suggestions ONLY in "vocabulary_tip", NEVER in "corrections".
2. TARGETED & MINIMAL CORRECTIONS:
   - "original" MUST be an exact verbatim substring found in the student's utterance.
   - "corrected" MUST only fix the specific broken words without rewriting the rest of the clause.
   - If there is no genuine mistake, do NOT return any corrections.
3. ERROR CATEGORIES:
   - 'grammar': Definite grammatical errors (tenses, subject-verb agreement, articles, missing prepositions, plurals).
   - 'vocabulary': Clear word misuse or false friends (e.g. 'make homework' instead of 'do homework').
   - 'fluency': Broken, confusing, or ungrammatical word order.

## Few-Shot Reference Examples:

Example 1 — Utterance with Clear Errors:
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

Example 2 — Natural Spoken Utterance (NO ERRORS -> corrections MUST BE EMPTY):
Student: "I want to practice my English speaking skills with you."
JSON:
{{
  "grammar_score": 98,
  "vocabulary_score": 92,
  "fluency_score": 95,
  "corrections": [],
  "grammar_tip": "Your sentence structure and infinitive usage ('want to practice') are completely accurate!",
  "vocabulary_tip": "To expand {next_level} vocabulary, you could try phrases like 'hone my conversational skills'.",
  "fluency_tip": "Smooth rhythm and clear, direct phrasing.",
  "positive_note": "Flawless sentence! Your grammar is accurate and natural.",
  "tip": "Keep speaking with this level of clarity and confidence!"
}}

Example 3 — Short Conversational Answer (NO ERRORS -> corrections MUST BE EMPTY):
Student: "I am fine, how about you?"
JSON:
{{
  "grammar_score": 100,
  "vocabulary_score": 90,
  "fluency_score": 95,
  "corrections": [],
  "grammar_tip": "Perfect casual greeting grammar.",
  "vocabulary_tip": "You can also try greetings like 'I'm doing well' or 'Never better'.",
  "fluency_tip": "Natural conversational reciprocation.",
  "positive_note": "Friendly, polite, and completely accurate response!",
  "tip": "Great natural conversational flow."
}}

Respond ONLY with a valid JSON object matching this exact schema:

{{
  "grammar_score": <number 0-100>,
  "vocabulary_score": <number 0-100>,
  "fluency_score": <number 0-100>,
  "corrections": [
    {{
      "original": "<verbatim erroneous phrase from student only - leave array empty if no real errors>",
      "corrected": "<direct minimal correction fixing the error>",
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
---{context_block}
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

    def _get_client_and_model(self) -> tuple[AsyncOpenAI, str, str]:
        """Dynamically resolve client and model from fresh settings so .env changes apply live."""
        from app.config import Settings
        cfg = Settings()
        provider = cfg.ai_provider

        if provider == "local":
            return (
                AsyncOpenAI(
                    api_key="ollama",
                    base_url=cfg.ollama_base_url,
                ),
                cfg.local_llm_model,
                provider,
            )
        elif provider == "bifrost":
            return (
                AsyncOpenAI(
                    api_key=cfg.bifrost_api_key or "bk-milo-token-gateway",
                    base_url=cfg.bifrost_base_url,
                    default_headers={"X-Bifrost-App": "MILO-AI-Backend"},
                ),
                cfg.bifrost_model,
                provider,
            )
        elif provider == "groq":
            return (
                AsyncOpenAI(
                    api_key=cfg.groq_api_key or "missing_groq_key",
                    base_url=cfg.groq_base_url,
                ),
                cfg.groq_model,
                provider,
            )
        elif provider == "openrouter":
            return (
                AsyncOpenAI(
                    api_key=cfg.openrouter_api_key or "missing_key",
                    base_url=cfg.openrouter_base_url,
                    default_headers={
                        "HTTP-Referer": "http://localhost:8000",
                        "X-Title": "MILO AI English Tutor",
                    },
                ),
                cfg.openrouter_model,
                provider,
            )
        else:
            return (
                AsyncOpenAI(api_key=cfg.openai_api_key),
                cfg.llm_model,
                provider,
            )

    async def analyze(
        self,
        user_text: str,
        cefr_level: str = "B1",
        topic: Optional[str] = None,
        context: Optional[str] = None,
    ) -> FeedbackResult:
        """
        Analyze a user's utterance and return structured language feedback.

        Args:
            user_text: The user's spoken/typed English text.
            cefr_level: Target CEFR level for evaluation context.
            topic: Practice topic or scenario name.
            context: Preceding conversation utterance for context awareness.

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

        client, model, provider = self._get_client_and_model()
        next_level = _LEVEL_PROGRESSION.get(cefr_level, "C1")

        system_prompt = FEEDBACK_SYSTEM_PROMPT.format(
            cefr_level=cefr_level,
            next_level=next_level,
        )

        context_lines = []
        if topic:
            context_lines.append(f"Scenario Topic: {topic}")
        if context:
            context_lines.append(f"Preceding Tutor Question: {context}")
        context_block = ("\n" + "\n".join(context_lines)) if context_lines else ""

        user_prompt = FEEDBACK_USER_PROMPT.format(
            user_text=user_text.strip(),
            context_block=context_block,
        )

        extra_kwargs = {}
        if provider == "openrouter":
            from app.config import Settings
            cfg = Settings()
            extra_kwargs["extra_body"] = {
                "reasoning": {"max_tokens": 0},
                "models": cfg.openrouter_model_list,
                "route": "fallback",
            }

        try:
            try:
                completion = await client.chat.completions.create(
                    model=model,
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
                    completion = await client.chat.completions.create(
                        model=model,
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
            if provider == "openrouter" and model != "openrouter/free":
                try:
                    logger.info("Attempting feedback fallback to 'openrouter/free'...")
                    completion = await client.chat.completions.create(
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
            return self._parse_result(data, user_text=user_text)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback regex/slice for { ... } if markdown contained chatter
            start = clean_content.find("{")
            end = clean_content.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    data = json.loads(clean_content[start : end + 1])
                    return self._parse_result(data, user_text=user_text)
                except Exception:
                    pass
            logger.error(f"Failed to parse feedback JSON: {e}\nRaw: {raw_content[:200]}")
            return self._fallback_result()

    def _parse_result(self, data: dict, user_text: str = "") -> FeedbackResult:
        """Parse raw JSON dict into a validated FeedbackResult with false-positive filtering."""
        corrections = []
        user_lower = user_text.lower()

        for c in data.get("corrections", []):
            orig = (c.get("original") or "").strip()
            corr = (c.get("corrected") or "").strip()
            if not orig or not corr:
                continue

            clean_orig = orig.strip(".,!?\"' ")
            clean_corr = corr.strip(".,!?\"' ")

            # Skip identity or punctuation-only corrections
            if clean_orig.lower() == clean_corr.lower():
                continue

            # Ensure the flagged phrase actually exists in the student's utterance
            orig_words = [w for w in clean_orig.lower().split() if w]
            if orig_words:
                orig_found = clean_orig.lower() in user_lower or all(w in user_lower for w in orig_words)
                if not orig_found:
                    logger.debug(f"Discarding hallucinated correction phrase not in utterance: '{orig}'")
                    continue

            et = (c.get("error_type") or "grammar").strip().lower()
            if "vocab" in et:
                et = "vocabulary"
            elif "fluen" in et:
                et = "fluency"
            else:
                et = "grammar"

            corrections.append(
                CorrectionItem(
                    original=orig,
                    corrected=corr,
                    explanation=(c.get("explanation") or "").strip(),
                    error_type=et,
                )
            )

        raw_grammar = float(data.get("grammar_score", 85.0))
        raw_vocab = float(data.get("vocabulary_score", 85.0))
        raw_fluency = float(data.get("fluency_score", 85.0))

        # If no legitimate errors exist, ensure user is not penalized unfairly
        if not corrections:
            raw_grammar = max(raw_grammar, 94.0)
            raw_vocab = max(raw_vocab, 90.0)
            raw_fluency = max(raw_fluency, 90.0)

        return FeedbackResult(
            grammar_score=raw_grammar,
            vocabulary_score=raw_vocab,
            fluency_score=raw_fluency,
            corrections=corrections,
            positive_note=data.get("positive_note", "Good effort!"),
            tip=data.get("tip", "Keep practicing!"),
            grammar_tip=data.get("grammar_tip", "Sentence structure and grammar are solid."),
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
    topic: Optional[str] = None,
    context: Optional[str] = None,
) -> FeedbackResult:
    """High-level feedback analysis helper used by the pipeline."""
    return await feedback_engine.analyze(
        user_text=user_text,
        cefr_level=cefr_level,
        topic=topic,
        context=context,
    )

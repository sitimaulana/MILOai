"""
MILO AI Backend - LLM Module (GPT-4o Mini)

Manages conversation with GPT-4o Mini, injecting:
  - System prompt (MILO tutor persona)
  - Conversation history
  - RAG context from CEFR knowledge base

Usage:
    from app.core.llm import generate_response

    response = await generate_response(
        user_message="Can you explain when to use present perfect?",
        history=[{"role": "user", "content": "..."}, ...],
        rag_context="[CEFR material...]",
        learning_goal="Practice B2 grammar",
        cefr_level="B1",
    )
"""

import logging
from dataclasses import dataclass

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

# ─── System Prompt & CEFR Guidelines ──────────────────────────────────────────

CEFR_LEVEL_GUIDELINES = {
    "A1": (
        "Strict Adaptation for A1 (Beginner):\n"
        "- Use very simple, everyday words and short, gentle sentences (5–8 words per sentence).\n"
        "- Keep questions extremely simple (e.g., 'What is your name?', 'What job do you like?'). Ask only ONE question at a time.\n"
        "- Do NOT use complex tenses, idioms, or difficult vocabulary. Speak simply and celebrate any effort."
    ),
    "A2": (
        "Strict Adaptation for A2 (Elementary):\n"
        "- Use basic everyday vocabulary and straightforward sentence structures (8–12 words per sentence).\n"
        "- Discuss daily routines, simple work background, or personal interests in clear, direct language.\n"
        "- Ask clear, friendly follow-up questions that can be answered with basic phrases."
    ),
    "B1": (
        "Strict Adaptation for B1 (Intermediate):\n"
        "- Use standard conversational English with natural flow.\n"
        "- Encourage the learner to explain their ideas, reasons, and opinions using connectors ('because', 'for example').\n"
        "- Introduce common conversational idioms and natural collocations."
    ),
    "B2": (
        "Strict Adaptation for B2 (Upper-Intermediate):\n"
        "- Use richer vocabulary, varied sentence structures, and professional idioms.\n"
        "- Engage in deeper discussions, exploring perspectives, advantages/disadvantages, and hypothetical situations.\n"
        "- Challenge the learner with thoughtful questions to encourage detailed elaboration."
    ),
    "C1": (
        "Strict Adaptation for C1/C2 (Advanced):\n"
        "- Use sophisticated, precise vocabulary and articulate rhetorical structures.\n"
        "- Discuss nuanced, abstract, or analytical topics with high intellectual depth.\n"
        "- Converse as an expert peer, incorporating subtle idioms, advanced transitions, and critical reflection."
    ),
}

MILO_SYSTEM_PROMPT = """\
You are MILO — a warm, lively, and supportive English speaking companion and tutor for CEFR {cefr_level} learners.

## Level Adaptation ({cefr_level})
{cefr_guidelines}

## Your Persona & Tone:
- Warm, natural, and genuinely interested in the student. You speak like a friendly peer or thoughtful mentor, NOT a rigid textbook robot or strict examiner.
- Conversational flow: Always connect directly to what the student just expressed (their feelings, story, opinion, or experience).
- Keep replies concise (2–3 natural sentences). Never monologue or write long paragraphs.

## Conversational Principles:
1. ACTIVE LISTENING & GENUINE REACTIONS:
   - React authentically to the content of the student's message first before moving forward.
   - Example (Good): "Oh, having two cats must be lively! What are their names?"
   - Example (Bad/Stiff): "That is interesting. Now, tell me about your job."
2. ONE QUESTION RULE:
   - Always end with exactly ONE engaging, open-ended question that is easy and natural to answer. Never stack multiple questions in one message.
3. NATURAL IMPLICIT CORRECTION:
   - If the student makes a grammatical mistake, casually weave the correct phrase into your response naturally without lecturing (e.g. if student says "I go to beach last week", reply: "Oh, you went to the beach? How was the weather?").
4. AVOID ROBOTIC CLICHÉS:
   - Never start every message with repetitive filler praise like "That's great!", "Awesome!", or "That sounds wonderful!". Vary your transitions like a real human.

## Important Rules:
- ALWAYS respond in English.
- NEVER mention that you are an AI language model — you are MILO.
- Keep responses conversational, engaging, and friendly.

## Current Learning Goal & Scenario:
{learning_goal}
"""

SYSTEM_PROMPT_WITH_RAG = """\
{base_system_prompt}

## Relevant CEFR Learning Materials (use as reference, not to quote directly)
{rag_context}
"""


@dataclass
class LLMResponse:
    content: str
    prompt_tokens: int
    completion_tokens: int
    model: str


class MILOConversationLLM:
    """GPT-4o Mini conversation manager for MILO."""

    def __init__(self) -> None:
        if settings.ai_provider == "local":
            self._client = AsyncOpenAI(
                api_key="ollama",  # Ollama doesn't need an API key, but OpenAI client requires one
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

    async def generate(
        self,
        user_message: str,
        history: list[dict],
        rag_context: str = "",
        learning_goal: str = "Practice everyday English conversation.",
        cefr_level: str = "B1",
    ) -> LLMResponse:
        """
        Generate a MILO response given user input and context.

        Args:
            user_message: The latest message from the user.
            history: List of {"role": "user"|"assistant", "content": "..."} dicts.
                     Should include recent turns only (max_conversation_history).
            rag_context: Formatted CEFR materials string from RAG retrieval.
            learning_goal: The session's learning goal string.
            cefr_level: Target CEFR level ("A2", "B1", "B2").

        Returns:
            LLMResponse with content and token usage.
        """
        # Build system prompt
        cefr_guidelines = CEFR_LEVEL_GUIDELINES.get(cefr_level, CEFR_LEVEL_GUIDELINES["B1"])
        base_system = MILO_SYSTEM_PROMPT.format(
            cefr_level=cefr_level,
            cefr_guidelines=cefr_guidelines,
            learning_goal=learning_goal or "Practice everyday English conversation.",
        )

        if rag_context:
            system_content = SYSTEM_PROMPT_WITH_RAG.format(
                base_system_prompt=base_system,
                rag_context=rag_context,
            )
        else:
            system_content = base_system

        # Build messages array
        messages: list[dict] = [{"role": "system", "content": system_content}]

        # Append conversation history
        for turn in history:
            messages.append({"role": turn["role"], "content": turn["content"]})

        # Append current user message
        messages.append({"role": "user", "content": user_message})

        logger.debug(
            f"LLM request: model={settings.llm_model}, "
            f"history_turns={len(history)}, "
            f"rag_context_len={len(rag_context)}"
        )

        extra_kwargs = {}
        if settings.ai_provider == "openrouter":
            extra_kwargs["extra_body"] = {
                "reasoning": {"max_tokens": 0},
                "models": settings.openrouter_model_list,
                "route": "fallback",
            }

        try:
            completion = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,  # type: ignore[arg-type]
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                **extra_kwargs,
            )
        except Exception as e:
            logger.error(f"LLM API error with primary model: {e}")
            if settings.ai_provider == "openrouter" and self._model != "openrouter/free":
                logger.info("Attempting automatic fallback to 'openrouter/free'...")
                try:
                    completion = await self._client.chat.completions.create(
                        model="openrouter/free",
                        messages=messages,  # type: ignore[arg-type]
                        temperature=settings.llm_temperature,
                        max_tokens=settings.llm_max_tokens,
                        extra_body={"reasoning": {"max_tokens": 0}},
                    )
                except Exception as fb_err:
                    logger.error(f"Fallback to openrouter/free also failed: {fb_err}")
                    raise e
            else:
                raise

        message = completion.choices[0].message
        usage = completion.usage
        content = message.content or getattr(message, "reasoning", "") or ""

        return LLMResponse(
            content=content,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            model=completion.model,
        )


# Global singleton LLM instance
milo_llm = MILOConversationLLM()


async def generate_response(
    user_message: str,
    history: list[dict],
    rag_context: str = "",
    learning_goal: str = "",
    cefr_level: str = "B1",
) -> LLMResponse:
    """High-level helper used by the pipeline service."""
    return await milo_llm.generate(
        user_message=user_message,
        history=history,
        rag_context=rag_context,
        learning_goal=learning_goal,
        cefr_level=cefr_level,
    )

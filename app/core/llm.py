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
import re
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
You are MILO, a warm, lively, and supportive English speaking companion and tutor for CEFR {cefr_level} learners.

## Level Adaptation ({cefr_level})
{cefr_guidelines}

## Your Persona & Tone:
- Warm, natural, and genuinely interested in the student. You speak like a friendly peer or thoughtful mentor, NOT a rigid textbook robot or strict examiner.
- Conversational flow: Always connect directly to what the student just expressed (their feelings, story, opinion, or experience).
- Spoken conciseness: Keep replies concise (2–3 natural spoken sentences, max 40 words total). Never monologue or write long paragraphs.

## Conversational Principles:
1. ACTIVE LISTENING & STRICT GROUNDING:
   - React authentically and strictly to what the student just said in their latest message.
   - Do NOT invent unmentioned topics, assume fake scenarios, or jump to unrelated subjects.
   - Example (Good): "Oh, having two cats must be lively! What are their names?"
   - Example (Bad/Stiff): "That is interesting. Now, tell me about your job."
2. SINGLE CONVERSATIONAL QUESTION:
   - Always conclude with exactly ONE engaging, open-ended question that is easy and natural to answer. Never stack multiple questions in one message.
3. NO UNSOLICITED LECTURING:
   - Never give unrequested grammar lectures, quiz the user out of the blue, or explain textbook rules unless the student explicitly asks ("How do I use...", "Explain...", "What is the difference...").
4. NATURAL IMPLICIT RECASTING:
   - If the student makes a minor mistake, casually weave the correct phrase into your response naturally without lecturing (e.g. if student says "I go to beach last week", reply: "Oh, you went to the beach? How was the weather?").
5. AVOID ROBOTIC CLICHÉS:
   - Never start every message with repetitive filler praise like "That's great!", "Awesome!", or "That sounds wonderful!". Vary your transitions like a real human.

## Important Rules:
- ALWAYS respond in English.
- NEVER mention that you are an AI language model: you are MILO.
- Keep responses conversational, engaging, and friendly.
- Output ONLY direct conversational speech. NEVER include meta-commentary, constraint checklists, rule explanations, or bracketed/italicized notes about your instructions (e.g., do NOT output "*One question rule applies.*", "*Rule applied*", or any notes in asterisks or parentheses explaining system prompt rules).

## Current Learning Goal & Scenario:
{learning_goal}
"""

SYSTEM_PROMPT_WITH_RAG = """\
{base_system_prompt}

## Verified Reference Knowledge & Strict Grounding Rules:
{rag_context}

## Strict Grounding & Pedagogical Directives:
1. STRICT FACTUAL GROUNDING: Base your grammatical, lexical, and pedagogical explanations strictly on the verified reference material above. Do NOT invent, assume, or hallucinate non-standard grammatical rules.
2. NATURAL SPOKEN RECASTING: Provide a clear, natural explanation (1-2 sentences), give 1 practical conversational example, and always conclude with exactly ONE engaging question for the student to practice.
3. CAUTIOUS FALLBACK: If the student asks about a concept not covered in the reference material, answer courteously using standard CEFR {cefr_level} conversational English without making up unsupported textbook citations.
"""

CLOSING_DIRECTIVE = """\
## CRITICAL DIRECTIVE - SESSION TIME LIMIT REACHED:
The practice session duration has ended. This is the FINAL turn of the conversation.
You MUST conclude the conversation:
1. NO QUESTIONS AT CLOSING: DO NOT ask any questions! Do not ask "What about you?", "How about you?", or anything that invites a reply. Under NO circumstances should you include a question mark (?).
2. ACKNOWLEDGE TIME: State warmly and naturally that our practice time for today has finished.
3. PRAISE & ENCOURAGE: Commend the student for their spoken participation and effort today in 1-2 natural, spoken sentences.
4. SIGN OFF: Conclude with a warm sign-off (e.g., "Take care, and see you next time!").
"""


@dataclass
class LLMResponse:
    content: str
    prompt_tokens: int
    completion_tokens: int
    model: str


class MILOConversationLLM:
    """GPT-4o Mini conversation manager for MILO."""

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

    async def generate(
        self,
        user_message: str,
        history: list[dict],
        rag_context: str = "",
        learning_goal: str = "Practice everyday English conversation.",
        cefr_level: str = "B1",
        is_closing: bool = False,
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
            is_closing: Whether to instruct MILO to conclude the session without questions.

        Returns:
            LLMResponse with content and token usage.
        """
        client, model, provider = self._get_client_and_model()

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

        if is_closing:
            system_content = f"{system_content}\n\n{CLOSING_DIRECTIVE}"

        # Build messages array
        messages: list[dict] = [{"role": "system", "content": system_content}]

        # Append conversation history
        for turn in history:
            messages.append({"role": turn["role"], "content": turn["content"]})

        # Append current user message
        messages.append({"role": "user", "content": user_message})

        logger.debug(
            f"LLM request: provider={provider}, model={model}, "
            f"history_turns={len(history)}, "
            f"rag_context_len={len(rag_context)}"
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
            completion = await client.chat.completions.create(
                model=model,
                messages=messages,  # type: ignore[arg-type]
                temperature=min(settings.llm_temperature, 0.45),
                max_tokens=settings.llm_max_tokens,
                **extra_kwargs,
            )
        except Exception as e:
            err_msg = str(e).lower()
            logger.error(f"LLM API error with primary model {model}: {e}")

            # Check if this is a 401 Unauthorized / User not found error
            if "401" in err_msg or "unauthorized" in err_msg or "user not found" in err_msg:
                fallback_msg = (
                    "⚠️ [Autentikasi Gagal 401] API Key Anda tidak valid atau salah salin (User not found). "
                    "Silakan periksa kembali nilai API Key di file .env."
                )
                return LLMResponse(
                    content=fallback_msg,
                    prompt_tokens=0,
                    completion_tokens=0,
                    model=f"{model} (Auth Error 401)",
                )

            # Check if this is a 429 rate limit error
            if "429" in err_msg or "rate limit" in err_msg or "quota" in err_msg:
                fallback_msg = (
                    "⚠️ [Batas Kuota Tercapai] Kuota harian API model AI Anda saat ini telah mencapai batas (Error 429). "
                    "Silakan ganti API Key dari akun OpenRouter baru atau beralih ke provider Groq di file .env untuk kuota tanpa batas!"
                )
                return LLMResponse(
                    content=fallback_msg,
                    prompt_tokens=0,
                    completion_tokens=0,
                    model=f"{model} (Rate Limited 429)",
                )

            if provider == "openrouter" and model != "openrouter/free":
                logger.info("Attempting automatic fallback to 'openrouter/free'...")
                try:
                    completion = await client.chat.completions.create(
                        model="openrouter/free",
                        messages=messages,  # type: ignore[arg-type]
                        temperature=min(settings.llm_temperature, 0.45),
                        max_tokens=settings.llm_max_tokens,
                        extra_body={"reasoning": {"max_tokens": 0}},
                    )
                except Exception as fb_err:
                    fb_str = str(fb_err).lower()
                    logger.error(f"Fallback to openrouter/free also failed: {fb_err}")
                    if "429" in fb_str or "rate limit" in fb_str:
                        return LLMResponse(
                            content="⚠️ [Batas Kuota Tercapai] Seluruh kuota gratis OpenRouter untuk akun ini telah habis (Error 429). Silakan gunakan provider Groq atau akun OpenRouter baru di file .env.",
                            prompt_tokens=0,
                            completion_tokens=0,
                            model="openrouter/free (Rate Limited 429)",
                        )
                    raise e
            else:
                raise

        message = completion.choices[0].message
        usage = completion.usage
        raw_content = message.content or getattr(message, "reasoning", "") or ""
        content = sanitize_llm_response(raw_content)

        return LLMResponse(
            content=content,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            model=completion.model,
        )


def sanitize_llm_response(text: str) -> str:
    """
    Clean unwanted meta-commentary, instruction leakage, or rule tags
    from LLM responses before returning to pipeline/TTS.
    """
    if not text:
        return ""
    patterns = [
        r"(?i)[-*•]?\s*\*+\s*\(?\s*(?:note:?\s*)?(?:one|single)\s+question\s+rule\b[^*\n]*\)?\s*\*+\.?",
        r"(?i)[-*•]?\s*[\(\[]\s*(?:note:?\s*)?(?:one|single)\s+question\s+rule\b[^)\]\n]*[\)\]]\.?",
        r"(?i)\*+\s*\(?\s*(?:note:?\s*)?rule\s+\d+\s+(?:applies|applied|enforced)[^*\n]*\)?\s*\*+\.?",
        r"(?i)(?:note:?\s*)?(?:one|single)\s+question\s+rule\s+applies\.?",
    ]
    cleaned = text
    for pattern in patterns:
        cleaned = re.sub(pattern, "", cleaned)
    return cleaned.strip()


# Global singleton LLM instance
milo_llm = MILOConversationLLM()


async def generate_response(
    user_message: str,
    history: list[dict],
    rag_context: str = "",
    learning_goal: str = "",
    cefr_level: str = "B1",
    is_closing: bool = False,
) -> LLMResponse:
    """High-level helper used by the pipeline service."""
    return await milo_llm.generate(
        user_message=user_message,
        history=history,
        rag_context=rag_context,
        learning_goal=learning_goal,
        cefr_level=cefr_level,
        is_closing=is_closing,
    )

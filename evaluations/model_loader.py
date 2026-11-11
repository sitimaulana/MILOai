"""
MILO AI Backend - DeepEval LLM Judge Loader

Automatically configures the LLM-as-a-Judge based on app settings:
- OpenRouter (if AI_PROVIDER=openrouter)
- Bifrost Gateway (if AI_PROVIDER=bifrost)
- Local Ollama (if AI_PROVIDER=local)
- OpenAI (if AI_PROVIDER=openai or OPENAI_API_KEY present)
"""

import os
import logging
from typing import Optional
from deepeval.models import OpenAIModel
from app.config import settings

logger = logging.getLogger(__name__)


def get_eval_judge_model(
    override_model: Optional[str] = None,
    override_base_url: Optional[str] = None,
    override_api_key: Optional[str] = None,
) -> OpenAIModel:
    """
    Returns an OpenAIModel configured for DeepEval evaluation metrics.
    Adapts automatically to the project's AI provider in .env.
    """
    # Environment variable overrides
    env_eval_model = os.getenv("EVAL_MODEL") or override_model
    env_api_key = os.getenv("EVAL_API_KEY") or override_api_key
    env_base_url = os.getenv("EVAL_BASE_URL") or override_base_url

    if env_eval_model and env_api_key:
        return OpenAIModel(
            model=env_eval_model,
            api_key=env_api_key,
            base_url=env_base_url,
        )

    # Provider-based detection
    provider = settings.ai_provider.lower()

    if provider == "openrouter":
        model_name = env_eval_model or settings.openrouter_model
        api_key = env_api_key or settings.openrouter_api_key
        base_url = env_base_url or settings.openrouter_base_url
        logger.info(f"Using OpenRouter model as DeepEval Judge: {model_name}")
        return OpenAIModel(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
        )

    elif provider == "bifrost":
        model_name = env_eval_model or settings.bifrost_model
        api_key = env_api_key or settings.bifrost_api_key or "bk-milo-token-gateway"
        base_url = env_base_url or settings.bifrost_base_url
        logger.info(f"Using Bifrost Gateway model as DeepEval Judge: {model_name}")
        return OpenAIModel(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
        )

    elif provider == "local":
        model_name = env_eval_model or settings.local_llm_model
        base_url = env_base_url or settings.ollama_base_url
        logger.info(f"Using Ollama local model as DeepEval Judge: {model_name}")
        return OpenAIModel(
            model=model_name,
            api_key="ollama",
            base_url=base_url,
        )

    else:
        # Default to OpenAI direct
        model_name = env_eval_model or settings.llm_model
        api_key = env_api_key or settings.openai_api_key or os.getenv("OPENAI_API_KEY", "")
        logger.info(f"Using OpenAI model as DeepEval Judge: {model_name}")
        return OpenAIModel(
            model=model_name,
            api_key=api_key,
        )


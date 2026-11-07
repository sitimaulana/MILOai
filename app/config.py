"""
MILO AI Backend - Application Configuration

Loads all settings from environment variables (.env file).
Uses pydantic-settings for type-safe configuration management.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ────────────────────────────────────────────────────────────────────
    app_name: str = "MILO AI Backend"
    app_version: str = "0.1.0"
    debug: bool = False
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    auto_translate_responses: bool = False  # Set to False for low latency (translate on-demand via UI button)

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    # ── AI Provider Mode ────────────────────────────────────────────────────────
    ai_provider: str = "local"  # "openai", "local" (Ollama), "openrouter", or "bifrost"

    # ── Bifrost Gateway (LLM Token & Rate-Limit Gateway) ───────────────────────
    bifrost_base_url: str = "http://localhost:8080/v1"
    bifrost_api_key: str = "bk-milo-token-gateway"
    bifrost_model: str = "openai/gpt-4o-mini"

    # ── OpenAI ─────────────────────────────────────────────────────────────────
    openai_api_key: str = ""  # Required only when AI_PROVIDER=openai

    # ── OpenRouter ─────────────────────────────────────────────────────────────
    openrouter_api_key: str = ""  # Required when AI_PROVIDER=openrouter
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "nvidia/nemotron-3.5-lightning:free"
    # Fallback models: if primary model is rate-limited, try these in order
    openrouter_fallback_models: str = "nvidia/nemotron-3-ultra-550b-a55b:free,google/gemma-4-26b-a4b-it:free,google/gemma-4-31b-it:free"

    @property
    def openrouter_model_list(self) -> list[str]:
        """Return [primary_model, ...fallbacks] for OpenRouter route=fallback (max 3 models)."""
        models = [self.openrouter_model]
        if self.openrouter_fallback_models:
            models.extend(m.strip() for m in self.openrouter_fallback_models.split(",") if m.strip())
        return models[:3]

    # ── LLM ───────────────────────────────────────────────────────────────────
    llm_model: str = "gpt-4o-mini"
    local_llm_model: str = "llama3.1"
    ollama_base_url: str = "http://localhost:11434/v1"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 512

    # ── Whisper (Local) ────────────────────────────────────────────────────────
    whisper_model_size: str = "base"
    whisper_device: str = "cpu"

    # ── TTS ───────────────────────────────────────────────────────────────────
    tts_model: str = "tts-1"
    tts_voice: str = "nova"

    # ── RAG / ChromaDB ─────────────────────────────────────────────────────────
    embedding_model: str = "text-embedding-3-small"
    chroma_db_path: str = "./knowledge_base/chroma_db"
    chroma_collection_name: str = "cefr_knowledge"
    rag_top_k: int = 3
    rag_chunk_size: int = 500
    rag_chunk_overlap: int = 50

    # ── PostgreSQL ─────────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/milo_db"
    database_url_sync: str = "postgresql+psycopg2://postgres:password@localhost:5432/milo_db"

    # ── Session ────────────────────────────────────────────────────────────────
    max_conversation_history: int = 20
    session_timeout_minutes: int = 60


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance (singleton pattern)."""
    return Settings()


# Shortcut import for convenience
settings = get_settings()

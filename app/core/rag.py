"""
MILO AI Backend - RAG Module (Retrieval-Augmented Generation)

Manages the ChromaDB vector store for CEFR B1-B2 knowledge retrieval.
Uses LangChain + OpenAI embeddings to find relevant learning materials.

Usage:
    from app.core.rag import retrieve_context

    docs = await retrieve_context("How do I use present perfect tense?", k=3)
    for doc in docs:
        print(doc.page_content, doc.metadata)
"""

import logging
from dataclasses import dataclass
from pathlib import Path

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class RetrievedContext:
    content: str
    source: str
    skill_type: str  # "grammar" | "vocabulary" | "speaking" | "general"
    cefr_level: str  # "B1" | "B2" | "B1-B2"
    relevance_score: float


class RAGRetriever:
    """
    Wrapper around ChromaDB for CEFR B1-B2 knowledge retrieval.
    
    The vector store is loaded once at startup and queried per request.
    Falls back gracefully if the vector store does not exist yet
    (i.e., before running knowledge_base/ingest.py).
    """

    _instance: "RAGRetriever | None" = None
    _vectorstore: Chroma | None = None
    _embeddings: OpenAIEmbeddings | HuggingFaceEmbeddings | None = None

    def __new__(cls) -> "RAGRetriever":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self) -> None:
        """Initialize embeddings and load ChromaDB vector store."""
        logger.info("Initializing RAG retriever...")

        if settings.ai_provider in ("local", "openrouter"):
            # Use local HuggingFace embeddings (all-MiniLM-L6-v2)
            self._embeddings = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2"
            )
        else:
            self._embeddings = OpenAIEmbeddings(
                model=settings.embedding_model,
                openai_api_key=settings.openai_api_key,
            )

        chroma_path = Path(settings.chroma_db_path)

        if not chroma_path.exists() or not any(chroma_path.iterdir()):
            logger.warning(
                f"⚠️  ChromaDB not found at '{chroma_path}'. "
                "RAG will return empty results until you run 'python knowledge_base/ingest.py'."
            )
            self._vectorstore = None
            return

        self._vectorstore = Chroma(
            collection_name=settings.chroma_collection_name,
            embedding_function=self._embeddings,
            persist_directory=str(chroma_path),
        )

        count = self._vectorstore._collection.count()
        logger.info(f"✅ RAG loaded — {count} documents in ChromaDB collection.")

    @property
    def is_ready(self) -> bool:
        return self._vectorstore is not None

    async def retrieve(
        self,
        query: str,
        k: int | None = None,
        skill_filter: str | None = None,
        cefr_level: str | None = None,
    ) -> list[RetrievedContext]:
        """
        Retrieve the top-k most relevant CEFR chunks for a given query.

        Args:
            query: The user's message or learning context query
            k: Number of documents to retrieve (defaults to settings.rag_top_k)
            skill_filter: Optional filter by skill type ("grammar", "vocabulary", "speaking")
            cefr_level: Optional filter by CEFR level ("B1", "B2")

        Returns:
            List of RetrievedContext, sorted by relevance (most relevant first).
        """
        if self._vectorstore is None:
            logger.debug("RAG vectorstore not ready, returning empty context.")
            return []

        k = k or settings.rag_top_k

        # Build metadata filter
        where_filter: dict | None = None
        if skill_filter or cefr_level:
            conditions = []
            if skill_filter:
                conditions.append({"skill_type": {"$eq": skill_filter}})
            if cefr_level:
                conditions.append({"cefr_level": {"$in": [cefr_level, "B1-B2"]}})

            if len(conditions) == 1:
                where_filter = conditions[0]
            elif len(conditions) > 1:
                where_filter = {"$and": conditions}

        try:
            results = self._vectorstore.similarity_search_with_relevance_scores(
                query=query,
                k=k,
                filter=where_filter,
            )
        except Exception as e:
            logger.error(f"RAG retrieval error: {e}")
            return []

        contexts = []
        for doc, score in results:
            ctx = RetrievedContext(
                content=doc.page_content,
                source=doc.metadata.get("source", "unknown"),
                skill_type=doc.metadata.get("skill_type", "general"),
                cefr_level=doc.metadata.get("cefr_level", "B1-B2"),
                relevance_score=float(score),
            )
            contexts.append(ctx)

        logger.debug(f"RAG retrieved {len(contexts)} chunks for query: '{query[:50]}...'")
        return contexts

    def format_context_for_prompt(self, contexts: list[RetrievedContext]) -> str:
        """
        Format retrieved contexts into a string for injection into the LLM prompt.
        """
        if not contexts:
            return ""

        parts = ["[RELEVANT CEFR LEARNING MATERIALS]"]
        for i, ctx in enumerate(contexts, 1):
            parts.append(
                f"\n--- Material {i} ({ctx.skill_type.upper()}, CEFR {ctx.cefr_level}) ---\n"
                f"{ctx.content}"
            )
        return "\n".join(parts)


# Global singleton
rag_retriever = RAGRetriever()


async def retrieve_context(
    query: str,
    k: int | None = None,
    skill_filter: str | None = None,
    cefr_level: str = "B1",
) -> list[RetrievedContext]:
    """High-level retrieval helper used by the pipeline."""
    return await rag_retriever.retrieve(query, k, skill_filter, cefr_level)

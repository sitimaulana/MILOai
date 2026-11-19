"""
MILO AI Backend - Adaptive Hybrid RAG Module (Retrieval-Augmented Generation)

Orchestrates multi-channel knowledge retrieval for CEFR B1-B2 language learning:
1. Dense Semantic Vector Search via ChromaDB (HuggingFace / OpenAI Embeddings)
2. Sparse Keyword & Lexical Search via BM25 Retriever
3. Reciprocal Rank Fusion (RRF) with scenario & priority boosting
4. Adaptive Query & Intent Router (Grounding, QA, Error Remediation, Casual)

Usage:
    from app.core.rag import rag_retriever, retrieve_adaptive, retrieve_context

    # Adaptive retrieval within a microlearning session:
    contexts = await retrieve_adaptive(
        query="Tell me about your previous job",
        cefr_level="B1",
        topic_name="job_interview",
        topic_id="A1",
    )
"""

import asyncio
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class RetrievedContext:
    """A single retrieved knowledge chunk with rich CEFR metadata."""
    content: str
    source: str
    skill_type: str  # "grammar" | "vocabulary" | "speaking" | "assessment" | "general"
    cefr_level: str  # "B1" | "B2" | "B1-B2"
    relevance_score: float
    topic_id: str = ""
    track_code: str = ""
    is_primary: bool = False


class AdaptiveQueryRouter:
    """
    Classifies learner utterances and session signals to choose the optimal RAG route.
    """

    QA_TRIGGERS = (
        "what is", "what are", "what does", "how do", "how to", "difference between",
        "can you explain", "could you explain", "explain", "meaning of", "grammar rule", "why do",
        "is it correct", "how should i say", "vocabulary for", "cefr",
        "what means", "tell me the difference", "tell me about", "which tense", "example of",
        "which is correct", "which one is correct", "how to say", "what does that mean",
        "give me an example", "can you teach me", "how can i use",
        "i don't understand", "i don't know when to use", "i'm confused about",
        "confused between", "could you clarify", "what's the rule for",
        "is that grammatically correct", "synonym for", "another word for",
        "antonym of", "idiom for", "collocation with", "phrasal verb for",
        "how do you pronounce", "how to pronounce", "word stress for",
        "why is that wrong", "why was that wrong", "what did i say wrong",
        "what did i do wrong", "why did you correct", "tips for", "advice on"
    )

    GRAMMAR_ENTITIES = (
        "present perfect", "past continuous", "future continuous", "past perfect",
        "present continuous", "past simple", "passive voice", "conditional",
        "reported speech", "relative clause", "modal verb", "modal of deduction",
        "gerund", "infinitive", "preposition", "phrasal verb", "collocation",
        "past modal", "used to", "would rather", "had better"
    )

    USAGE_DILEMMAS = (
        "borrow", "lend", "used to", "be used to", "get used to",
        "since or for", "since vs for", "few or little", "few vs little",
        "say or tell", "say vs tell", "affect or effect", "affect vs effect",
        "must or have to", "must vs have to", "do or make", "do vs make"
    )

    TRACK_MAP = {
        "job_interview": "TRACK_A",
        "academic_discussion": "TRACK_B",
        "daily_conversation": "TRACK_C",
    }

    @classmethod
    def extract_target_skill(cls, user_message: str) -> Optional[str]:
        """
        Infers the specific pedagogical skill from linguistic entity cues
        to narrow down the vector/BM25 search space.
        """
        msg = user_message.lower()
        if any(w in msg for w in ("pronounce", "pronunciation", "sound", "stress", "intonation")):
            return "pronunciation"
        if any(w in msg for w in ("hesitation", "filler", "fluency", "conversation", "speaking", "turn-taking", "interview")):
            return "speaking"
        if any(w in msg for w in ("tense", "grammar", "rule", "verb", "passive", "conditional", "clause", "preposition", "borrow", "lend")) or any(e in msg for e in cls.GRAMMAR_ENTITIES):
            return "grammar"
        if any(w in msg for w in ("vocabulary", "word", "synonym", "antonym", "collocation", "idiom", "phrase", "phrasal")):
            return "vocabulary"
        return None

    @classmethod
    def classify_intent(
        cls,
        user_message: str,
        topic_name: Optional[str] = None,
        topic_id: Optional[str] = None,
        detected_error: Optional[str] = None,
    ) -> str:
        """
        Multi-tier intent classifier:
          - "EXPLICIT_QA": Learner asked a conceptual, grammatical, or lexical question
          - "ERROR_REMEDIATION": Context required for recurring error correction / clarification
          - "SCENARIO_GROUNDING": Learner is practicing an active microlearning roleplay
          - "CASUAL_DIALOGUE": General conversational flow (bypasses RAG to save latency)
        """
        msg = user_message.lower().strip()
        
        # 1. Check explicit pedagogical inquiry triggers
        if any(trigger in msg for trigger in cls.QA_TRIGGERS):
            return "EXPLICIT_QA"
            
        # 2. Check linguistic entity keywords (e.g. "past continuous", "used to vs be used to")
        if any(entity in msg for entity in cls.GRAMMAR_ENTITIES) or any(pair in msg for pair in cls.USAGE_DILEMMAS):
            return "EXPLICIT_QA"

        # 3. Check error remediation signals
        if detected_error or any(w in msg for w in ("wrong", "mistake", "error", "incorrect")):
            return "ERROR_REMEDIATION"

        # 4. Check active scenario / microlearning roleplay
        if topic_id or topic_name:
            return "SCENARIO_GROUNDING"

        # 5. Default to casual small-talk
        return "CASUAL_DIALOGUE"


class RAGRetriever:
    """
    Adaptive Hybrid RAG Engine combining ChromaDB Dense Search,
    BM25 Sparse Search, and Reciprocal Rank Fusion (RRF).
    """

    _instance: Optional["RAGRetriever"] = None
    _vectorstore: Optional[Chroma] = None
    _bm25_retriever: Optional[BM25Retriever] = None
    _embeddings: Optional[OpenAIEmbeddings | HuggingFaceEmbeddings] = None
    _indexed_docs: List[Document] = field(default_factory=list)

    def __new__(cls) -> "RAGRetriever":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._indexed_docs = []
        return cls._instance

    def load(self) -> None:
        """Initialize embeddings, load ChromaDB, and build in-memory BM25 index."""
        logger.info("Initializing Adaptive Hybrid RAG retriever...")

        # 1. Select Embedding Model (Default to local free HuggingFace model)
        if settings.ai_provider in ("local", "openrouter") or (
            settings.ai_provider == "bifrost" and (not settings.openai_api_key or settings.openai_api_key.startswith("sk-your"))
        ):
            logger.info("RAG using local HuggingFace embeddings: 'all-MiniLM-L6-v2' (100% free & offline)")
            self._embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        else:
            logger.info(f"RAG using OpenAI embeddings: '{settings.embedding_model}'")
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
            self._bm25_retriever = None
            return

        # 2. Connect to ChromaDB Collection
        try:
            self._vectorstore = Chroma(
                collection_name=settings.chroma_collection_name,
                embedding_function=self._embeddings,
                persist_directory=str(chroma_path),
            )
            count = self._vectorstore._collection.count()
            logger.info(f"✅ Dense Vector Store loaded — {count} vectors in collection '{settings.chroma_collection_name}'.")

            # 3. Build in-memory BM25 Retriever from ChromaDB records for Hybrid Search
            self._build_bm25_index()
        except Exception as e:
            logger.error(f"❌ Failed to initialize vectorstore: {e}")
            self._vectorstore = None
            self._bm25_retriever = None

    def _build_bm25_index(self) -> None:
        """Extract all chunks from ChromaDB and construct a BM25 index."""
        if not self._vectorstore:
            return

        try:
            raw_data = self._vectorstore._collection.get(include=["documents", "metadatas"])
            texts = raw_data.get("documents", [])
            metas = raw_data.get("metadatas", [])

            docs = []
            for text, meta in zip(texts, metas):
                docs.append(Document(page_content=text, metadata=meta or {}))

            self._indexed_docs = docs
            if docs:
                self._bm25_retriever = BM25Retriever.from_documents(docs)
                self._bm25_retriever.k = 6
                logger.info(f"✅ Sparse BM25 index initialized with {len(docs)} documents.")
            else:
                self._bm25_retriever = None
        except Exception as e:
            logger.warning(f"⚠️ Could not build BM25 index: {e}. Falling back to dense-only retrieval.")
            self._bm25_retriever = None

    @property
    def is_ready(self) -> bool:
        return self._vectorstore is not None

    async def retrieve_adaptive(
        self,
        query: str,
        cefr_level: str = "B1",
        topic_name: Optional[str] = None,
        topic_id: Optional[str] = None,
        detected_error: Optional[str] = None,
        k: Optional[int] = None,
        alpha: float = 0.6,
    ) -> List[RetrievedContext]:
        """
        Adaptive Hybrid Retrieval:
        1. Classifies query intent
        2. Conducts Dense (Vector) + Sparse (BM25) searches
        3. Fuses results with Reciprocal Rank Fusion (RRF)
        4. Applies scenario & microlearning priority boosting
        """
        if not self.is_ready:
            return []

        k = k or settings.rag_top_k
        intent = AdaptiveQueryRouter.classify_intent(
            user_message=query,
            topic_name=topic_name,
            topic_id=topic_id,
            detected_error=detected_error,
        )

        logger.debug(f"Adaptive RAG Intent: {intent} (Topic: {topic_name}, ID: {topic_id}, Level: {cefr_level})")

        # In casual chatter without topic context, do not clutter prompt with textbook chunks
        if intent == "CASUAL_DIALOGUE" and not topic_name and not topic_id:
            return []

        # Prepare search queries and filters based on intent
        dense_query = query
        sparse_query = query
        where_filter: Optional[Dict[str, Any]] = None

        if intent == "SCENARIO_GROUNDING":
            # Augment query with scenario cues
            track_code = AdaptiveQueryRouter.TRACK_MAP.get(topic_name or "", "")
            dense_query = f"{topic_name or ''} {query}".strip()
            sparse_query = f"{topic_id or ''} {topic_name or ''} {query}".strip()

            # Filter by level and track if available
            conditions = [{"cefr_level": {"$in": [cefr_level, "B1-B2"]}}]
            if track_code:
                conditions.append({"track_code": {"$in": [track_code, ""]}})
            if len(conditions) == 1:
                where_filter = conditions[0]
            else:
                where_filter = {"$and": conditions}

        elif intent == "EXPLICIT_QA":
            target_skill = AdaptiveQueryRouter.extract_target_skill(query)
            skills = [target_skill] if target_skill else ["grammar", "vocabulary", "speaking", "pronunciation", "general"]
            where_filter = {
                "$and": [
                    {"skill_type": {"$in": skills}},
                    {"cefr_level": {"$in": [cefr_level, "B1-B2"]}},
                ]
            }

        elif intent == "ERROR_REMEDIATION":
            # Augment queries with error keyword for targeted remediation
            err = detected_error or "grammar error correction"
            dense_query = f"{err} {query}".strip()
            sparse_query = f"{err} {query}".strip()
            where_filter = {
                "$and": [
                    {"skill_type": {"$in": ["grammar", "vocabulary", "assessment", "general"]}},
                    {"cefr_level": {"$in": [cefr_level, "B1-B2"]}},
                ]
            }

        # ─── 1. Dense Semantic Retrieval ───────────────────────────────────────
        fetch_k = max(k * 2, 6)
        dense_results: List[Tuple[Document, float]] = []
        try:
            dense_results = await asyncio.to_thread(
                self._vectorstore.similarity_search_with_relevance_scores,
                query=dense_query,
                k=fetch_k,
                filter=where_filter,
            )
        except Exception as e:
            logger.warning(f"Dense vector search failed: {e}")

        # ─── 2. Sparse BM25 Retrieval ──────────────────────────────────────────
        sparse_results: List[Document] = []
        if self._bm25_retriever:
            try:
                sparse_results = await asyncio.to_thread(
                    self._bm25_retriever.invoke,
                    sparse_query,
                )
            except Exception as e:
                logger.warning(f"BM25 sparse search failed: {e}")

        # ─── 3. Reciprocal Rank Fusion (RRF) with Dynamic Thresholding ──────────
        doc_scores: Dict[str, Tuple[Document, float]] = {}
        rrf_constant = 60

        # Determine dynamic dense candidate floor based on query intent
        tau_dense = (
            settings.rag_dense_threshold_qa
            if intent in ("EXPLICIT_QA", "ERROR_REMEDIATION")
            else settings.rag_dense_threshold_scenario
        )

        # Dense ranking (filter out low-similarity candidates below dynamic threshold)
        for rank, (doc, sim_score) in enumerate(dense_results, 1):
            if float(sim_score) < tau_dense:
                continue
            doc_id = doc.page_content.strip()[:80]
            score = (alpha / (rrf_constant + rank)) + (float(sim_score) * 0.1)
            doc_scores[doc_id] = (doc, score)

        # Sparse ranking
        for rank, doc in enumerate(sparse_results, 1):
            doc_id = doc.page_content.strip()[:80]
            current_doc, current_score = doc_scores.get(doc_id, (doc, 0.0))
            bonus_score = (1.0 - alpha) / (rrf_constant + rank)
            doc_scores[doc_id] = (current_doc, current_score + bonus_score)

        # ─── 4. Priority & Scenario Boosting ───────────────────────────────────
        target_topic_id = (topic_id or "").upper()
        target_track = AdaptiveQueryRouter.TRACK_MAP.get(topic_name or "", "")

        ranked_items = []
        for doc_id, (doc, score) in doc_scores.items():
            meta = doc.metadata or {}
            boost = 1.0

            # Boost primary microlearning scenarios & grammar
            if meta.get("is_primary") in ("true", True):
                boost += 0.25
            if target_topic_id and meta.get("topic_id", "").upper() == target_topic_id:
                boost += 0.40
            if target_track and meta.get("track_code", "").upper() == target_track:
                boost += 0.20

            final_score = score * boost
            ranked_items.append((doc, final_score))

        # Sort descending by fused score
        ranked_items.sort(key=lambda x: x[1], reverse=True)

        # ─── 5. Dynamic Fused Confidence Gate ────────────────────────────────────
        # Suppress context if even the top candidate fails to clear the confidence floor
        if not ranked_items or ranked_items[0][1] < settings.rag_fused_min_score:
            top_score = ranked_items[0][1] if ranked_items else 0.0
            logger.info(
                f"🛡️ [DYNAMIC THRESHOLD GATE] Context suppressed: Top fused score {top_score:.4f} "
                f"< cutoff {settings.rag_fused_min_score} (Intent: {intent})"
            )
            return []

        contexts: List[RetrievedContext] = []
        for doc, score in ranked_items[:k]:
            meta = doc.metadata or {}
            contexts.append(
                RetrievedContext(
                    content=doc.page_content,
                    source=meta.get("source", "unknown"),
                    skill_type=meta.get("skill_type", "general"),
                    cefr_level=meta.get("cefr_level", "B1-B2"),
                    relevance_score=round(score, 4),
                    topic_id=meta.get("topic_id", ""),
                    track_code=meta.get("track_code", ""),
                    is_primary=meta.get("is_primary") in ("true", True),
                )
            )

        logger.debug(f"Adaptive Hybrid RAG selected {len(contexts)} chunks for: '{query[:40]}...'")
        return contexts

    async def retrieve(
        self,
        query: str,
        k: Optional[int] = None,
        skill_filter: Optional[str] = None,
        cefr_level: str = "B1",
        min_score: float = 0.70,
    ) -> List[RetrievedContext]:
        """
        Standard dense retrieval helper for backward compatibility with existing tests.
        """
        if not self.is_ready:
            return []

        k = k or settings.rag_top_k
        where_filter: Optional[Dict[str, Any]] = None
        if skill_filter or cefr_level:
            conditions = []
            if skill_filter:
                conditions.append({"skill_type": {"$eq": skill_filter}})
            if cefr_level:
                conditions.append({"cefr_level": {"$in": [cefr_level, "B1-B2"]}})
            where_filter = conditions[0] if len(conditions) == 1 else {"$and": conditions}

        try:
            results = await asyncio.to_thread(
                self._vectorstore.similarity_search_with_relevance_scores,
                query=query,
                k=k,
                filter=where_filter,
            )
        except Exception as e:
            logger.error(f"RAG retrieval error: {e}")
            return []

        contexts = []
        for doc, score in results:
            if float(score) < min_score:
                continue
            meta = doc.metadata or {}
            contexts.append(
                RetrievedContext(
                    content=doc.page_content,
                    source=meta.get("source", "unknown"),
                    skill_type=meta.get("skill_type", "general"),
                    cefr_level=meta.get("cefr_level", "B1-B2"),
                    relevance_score=float(score),
                    topic_id=meta.get("topic_id", ""),
                    track_code=meta.get("track_code", ""),
                    is_primary=meta.get("is_primary") in ("true", True),
                )
            )
        return contexts

    def format_context_for_prompt(self, contexts: List[RetrievedContext]) -> str:
        """
        Format retrieved contexts into concise, actionable instructions for the LLM.
        Enforces strict grounding to prevent non-standard grammar hallucinations.
        """
        if not contexts:
            return ""

        parts = [
            "[VERIFIED CEFR REFERENCE MATERIAL & KNOWLEDGE BASE]",
            "Strict Grounding Directive: Use the provided textbook reference as the authoritative factual basis.",
            "Do NOT invent or hallucinate non-standard grammatical rules. Integrate the target pattern concisely:",
        ]
        for i, ctx in enumerate(contexts, 1):
            topic_tag = f"Topic {ctx.topic_id} | " if ctx.topic_id else ""
            source_tag = f" | Source: {ctx.source}" if ctx.source else ""
            parts.append(
                f"\n--- Reference Item {i} ({topic_tag}{ctx.skill_type.upper()}, Level {ctx.cefr_level}{source_tag}) ---\n"
                f"{ctx.content}"
            )
        parts.append(
            "\nPedagogical Instruction: Weave 1 target phrase or rule into your reply when relevant. "
            "Never monologue or recite full textbook pages. Keep your spoken reply concise (2-3 natural sentences) and always end with ONE engaging question."
        )
        return "\n".join(parts)


# Global singleton instance
rag_retriever = RAGRetriever()


async def retrieve_context(
    query: str,
    k: Optional[int] = None,
    skill_filter: Optional[str] = None,
    cefr_level: str = "B1",
    min_score: float = 0.70,
) -> List[RetrievedContext]:
    """Standard dense retrieval helper."""
    return await rag_retriever.retrieve(query, k, skill_filter, cefr_level, min_score=min_score)


async def retrieve_adaptive(
    query: str,
    cefr_level: str = "B1",
    topic_name: Optional[str] = None,
    topic_id: Optional[str] = None,
    detected_error: Optional[str] = None,
    k: Optional[int] = None,
) -> List[RetrievedContext]:
    """Primary entry point for Adaptive Hybrid RAG in conversation pipeline."""
    return await rag_retriever.retrieve_adaptive(
        query=query,
        cefr_level=cefr_level,
        topic_name=topic_name,
        topic_id=topic_id,
        detected_error=detected_error,
        k=k,
    )

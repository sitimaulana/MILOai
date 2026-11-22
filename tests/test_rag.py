"""
MILO AI Backend - Unit & Integration Tests for Adaptive Hybrid RAG Module

Tests:
1. Intent classification via AdaptiveQueryRouter
2. Dense + Sparse BM25 Retrieval & Reciprocal Rank Fusion (RRF)
3. Microlearning scenario & CEFR level boosting
4. Prompt context formatting
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.documents import Document

from app.core.rag import (
    AdaptiveQueryRouter,
    RAGRetriever,
    RetrievedContext,
    retrieve_adaptive,
)


def test_intent_classification():
    """Verify that AdaptiveQueryRouter correctly maps user queries and context signals."""
    # 1. Explicit QA
    assert AdaptiveQueryRouter.classify_intent("What is the difference between will and going to?") == "EXPLICIT_QA"
    assert AdaptiveQueryRouter.classify_intent("Can you explain how to use the present perfect?") == "EXPLICIT_QA"
    assert AdaptiveQueryRouter.classify_intent("What does bottleneck mean?") == "EXPLICIT_QA"

    # 2. Error Remediation
    assert AdaptiveQueryRouter.classify_intent(
        "I go to market yesterday", detected_error="Subject-verb agreement error"
    ) == "ERROR_REMEDIATION"

    # 3. Scenario Grounding
    assert AdaptiveQueryRouter.classify_intent(
        "Tell me about your career background", topic_name="job_interview"
    ) == "SCENARIO_GROUNDING"
    assert AdaptiveQueryRouter.classify_intent(
        "I want to discuss my thesis results", topic_name="academic_discussion", topic_id="B1"
    ) == "SCENARIO_GROUNDING"

    # 4. Casual Dialogue
    assert AdaptiveQueryRouter.classify_intent("Hello Milo, how are you doing today?") == "CASUAL_DIALOGUE"


@pytest.mark.asyncio
async def test_adaptive_hybrid_retrieval_and_rrf():
    """Verify that Dense + Sparse BM25 fusion ranks primary microlearning chunks highest."""
    retriever = RAGRetriever.__new__(RAGRetriever)
    retriever._embeddings = MagicMock()
    retriever._vectorstore = MagicMock()

    # Mock Chroma vector search returns
    doc_primary = Document(
        page_content="Target Vocabulary: STAR method, bottleneck, take initiative.",
        metadata={
            "source": "07_scenarios/microlearning/A1_introducing_background.md",
            "topic_id": "A1",
            "track_code": "TRACK_A",
            "cefr_level": "B1",
            "skill_type": "speaking",
            "is_primary": True,
        },
    )
    doc_secondary = Document(
        page_content="General interview tips and pleasantries.",
        metadata={
            "source": "07_scenarios/job_interview_general.md",
            "topic_id": "",
            "track_code": "TRACK_A",
            "cefr_level": "B1",
            "skill_type": "speaking",
            "is_primary": False,
        },
    )

    retriever._vectorstore.similarity_search_with_relevance_scores = MagicMock(
        return_value=[(doc_secondary, 0.85), (doc_primary, 0.82)]
    )

    # Mock BM25 sparse search
    retriever._bm25_retriever = MagicMock()
    retriever._bm25_retriever.invoke = MagicMock(return_value=[doc_primary])

    # Run adaptive retrieval for Job Interview with target topic A1
    results = await retriever.retrieve_adaptive(
        query="I want to introduce my work background",
        cefr_level="B1",
        topic_name="job_interview",
        topic_id="A1",
        k=2,
    )

    assert len(results) == 2
    # Because doc_primary has is_primary: True and topic_id: A1, its boost should elevate it to rank #1
    assert results[0].topic_id == "A1"
    assert results[0].is_primary is True
    assert "STAR method" in results[0].content


def test_format_context_for_prompt():
    """Verify prompt formatting outputs clean pedagogical instructions."""
    retriever = RAGRetriever.__new__(RAGRetriever)
    contexts = [
        RetrievedContext(
            content="STAR method for answering behavioral questions.",
            source="A1_introducing_background.md",
            skill_type="speaking",
            cefr_level="B1",
            relevance_score=0.92,
            topic_id="A1",
            track_code="TRACK_A",
            is_primary=True,
        )
    ]

    formatted = retriever.format_context_for_prompt(contexts)
    assert "[VERIFIED CEFR REFERENCE MATERIAL & KNOWLEDGE BASE]" in formatted
    assert "Topic A1" in formatted
    assert "STAR method" in formatted
    assert "Pedagogical Instruction:" in formatted

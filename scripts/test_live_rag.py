"""
Live verification script for Adaptive Hybrid RAG in AI-MILO.
Queries ChromaDB (289 vectors) + BM25 Sparse Index.
"""

import asyncio
from app.core.rag import rag_retriever, retrieve_adaptive


async def main():
    print("⏳ Loading Adaptive Hybrid RAG retriever...")
    await asyncio.to_thread(rag_retriever.load)
    print(f"✅ RAG Ready: {rag_retriever.is_ready}")

    queries = [
        {
            "track": "job_interview",
            "level": "B1",
            "topic_id": "A1",
            "query": "Could you tell me a little bit about yourself and your career background?",
        },
        {
            "track": "academic_discussion",
            "level": "B2",
            "topic_id": "B1",
            "query": "What are your thoughts on ethical considerations and bias in AI technology?",
        },
        {
            "track": "daily_conversation",
            "level": "B1",
            "topic_id": "C1",
            "query": "How do you usually unwind and spend your free time after a long busy week?",
        },
        {
            "track": None,
            "level": "B1",
            "topic_id": None,
            "query": "What is the difference between present perfect and past simple?",
        },
    ]

    for item in queries:
        print(f"\n{'='*70}")
        print(f"🔎 QUERY: '{item['query']}'")
        print(f"🎯 Scenario: {item['track']}, Level: {item['level']}, Topic ID: {item['topic_id']}")

        contexts = await retrieve_adaptive(
            query=item["query"],
            cefr_level=item["level"],
            topic_name=item["track"],
            topic_id=item["topic_id"],
            k=2,
        )

        print(f"📦 Retrieved {len(contexts)} contexts:")
        for i, ctx in enumerate(contexts, 1):
            print(f"  [{i}] Source: {ctx.source}")
            print(f"      Topic ID: {ctx.topic_id} | Track: {ctx.track_code} | Level: {ctx.cefr_level} | Primary: {ctx.is_primary}")
            snippet = ctx.content.replace('\n', ' ')[:120]
            print(f"      Snippet: {snippet}...")

    print("\n✅ Live Adaptive Hybrid RAG verification finished successfully!")


if __name__ == "__main__":
    asyncio.run(main())

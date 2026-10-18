"""
MILO AI Backend - Knowledge Base Ingestion Script

Loads CEFR B1-B2 learning materials from knowledge_base/documents/
and indexes them into ChromaDB for RAG retrieval.

Usage:
    python knowledge_base/ingest.py
    python knowledge_base/ingest.py --reset    # Clears existing DB first
    python knowledge_base/ingest.py --docs-dir ./my_docs  # Custom directory

Usage:
    # Use the existing Knowledge Base MILO folder:
    python knowledge_base/ingest.py --docs-dir "./Knowledge Base MILO"

    # Or the specific version:
    python knowledge_base/ingest.py --docs-dir "./Knowledge Base MILO/MILO_Knowledge_Base_B1_B2_COMPLETE_2026"

    # Reset and re-ingest:
    python knowledge_base/ingest.py --docs-dir "./Knowledge Base MILO" --reset

Supported file formats: PDF, DOCX, TXT, MD
"""

import argparse
import logging
import shutil
import sys
from pathlib import Path

# Ensure the project root is in the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
)
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def load_documents(docs_dir: Path) -> list[Document]:
    """Load all documents from the specified directory."""
    if not docs_dir.exists():
        logger.error(f"Documents directory not found: {docs_dir}")
        sys.exit(1)

    all_docs: list[Document] = []

    # Load PDFs
    pdf_files = list(docs_dir.rglob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF file(s)")
    for pdf_path in pdf_files:
        try:
            loader = PyPDFLoader(str(pdf_path))
            docs = loader.load()
            # Tag each doc with skill type based on filename keywords
            for doc in docs:
                doc.metadata.update(_extract_metadata(pdf_path, docs_root=docs_dir))
            all_docs.extend(docs)
            logger.info(f"  ✅ Loaded: {pdf_path.name} ({len(docs)} pages)")
        except Exception as e:
            logger.warning(f"  ⚠️  Failed to load {pdf_path.name}: {e}")

    # Load DOCX
    docx_files = list(docs_dir.rglob("*.docx"))
    logger.info(f"Found {len(docx_files)} DOCX file(s)")
    for docx_path in docx_files:
        try:
            loader = UnstructuredWordDocumentLoader(str(docx_path))
            docs = loader.load()
            for doc in docs:
                doc.metadata.update(_extract_metadata(docx_path, docs_root=docs_dir))
            all_docs.extend(docs)
            logger.info(f"  ✅ Loaded: {docx_path.name} ({len(docs)} chunks)")
        except Exception as e:
            logger.warning(f"  ⚠️  Failed to load {docx_path.name}: {e}")

    # Load TXT and MD
    text_files = list(docs_dir.rglob("*.txt")) + list(docs_dir.rglob("*.md"))
    logger.info(f"Found {len(text_files)} TXT/MD file(s)")
    for txt_path in text_files:
        try:
            loader = TextLoader(str(txt_path), encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                doc.metadata.update(_extract_metadata(txt_path, docs_root=docs_dir))
            all_docs.extend(docs)
            logger.info(f"  ✅ Loaded: {txt_path.name} ({len(docs)} doc)")
        except Exception as e:
            logger.warning(f"  ⚠️  Failed to load {txt_path.name}: {e}")

    logger.info(f"\nTotal documents loaded: {len(all_docs)}")
    return all_docs


def _extract_metadata(file_path: Path, docs_root: Path | None = None) -> dict:
    """
    Infer metadata (skill_type, cefr_level) from the file path.
    
    Supports both:
    1. Flat naming: grammar_B1_present_perfect.pdf
    2. Nested directories: 02_grammar/B1/present_perfect.md  (existing KB structure)
    """
    # Use the full relative path for richer context
    if docs_root:
        try:
            rel_path = str(file_path.relative_to(docs_root)).lower().replace("\\", "/")
        except ValueError:
            rel_path = str(file_path).lower()
    else:
        rel_path = str(file_path).lower()

    name = file_path.stem.lower()
    combined = f"{rel_path} {name}"  # Search in both path and filename

    # Detect skill type (from directory name or filename)
    if any(k in combined for k in ["grammar", "02_grammar"]):
        skill_type = "grammar"
    elif any(k in combined for k in ["vocabulary", "vocab", "03_vocabulary"]):
        skill_type = "vocabulary"
    elif any(k in combined for k in ["speaking", "conversation", "04_speaking", "07_scenarios"]):
        skill_type = "speaking"
    elif any(k in combined for k in ["pronunciation", "05_pronunciation"]):
        skill_type = "pronunciation"
    elif any(k in combined for k in ["feedback", "06_feedback", "assessment", "09_assessment"]):
        skill_type = "assessment"
    elif any(k in combined for k in ["rag", "08_rag", "cefr", "01_cefr"]):
        skill_type = "general"
    elif "writing" in combined:
        skill_type = "writing"
    else:
        skill_type = "general"

    # Detect CEFR level (from directory path OR filename)
    if "/b2/" in rel_path or "/b2 " in rel_path or "_b2_" in combined or combined.endswith("_b2"):
        cefr_level = "B2"
    elif "/b1/" in rel_path or "/b1 " in rel_path or "_b1_" in combined or combined.endswith("_b1"):
        cefr_level = "B1"
    elif "/a2/" in rel_path or "_a2_" in combined:
        cefr_level = "A2"
    else:
        cefr_level = "B1-B2"  # Default: applicable to both levels

    return {
        "source": file_path.name,
        "source_path": rel_path,
        "skill_type": skill_type,
        "cefr_level": cefr_level,
    }


def split_documents(documents: list[Document], chunk_size: int, chunk_overlap: int) -> list[Document]:
    """Split documents into chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"Split into {len(chunks)} chunks (size={chunk_size}, overlap={chunk_overlap})")
    return chunks


def ingest_to_chroma(
    chunks: list[Document],
    chroma_path: Path,
    collection_name: str,
) -> Chroma:
    """Embed chunks and store in ChromaDB."""
    if settings.ai_provider in ("local", "openrouter"):
        logger.info("Generating embeddings using local 'all-MiniLM-L6-v2' (HuggingFace)...")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    else:
        logger.info(f"Generating embeddings using '{settings.embedding_model}' (OpenAI)...")
        embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
        )

    logger.info(f"Storing {len(chunks)} chunks in ChromaDB at '{chroma_path}'...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=str(chroma_path),
    )

    count = vectorstore._collection.count()
    logger.info(f"✅ ChromaDB collection '{collection_name}' now has {count} vectors.")
    return vectorstore


def main() -> None:
    parser = argparse.ArgumentParser(description="MILO Knowledge Base Ingestion")
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path(__file__).parent / "documents",
        help="Directory containing CEFR learning materials",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear existing ChromaDB before ingestion",
    )
    args = parser.parse_args()

    chroma_path = Path(settings.chroma_db_path)

    # Optionally reset the vector store
    if args.reset and chroma_path.exists():
        logger.info(f"🗑️  Resetting ChromaDB at '{chroma_path}'...")
        shutil.rmtree(chroma_path)
        logger.info("ChromaDB cleared.")

    chroma_path.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("MILO Knowledge Base Ingestion")
    logger.info("=" * 60)
    logger.info(f"Documents directory : {args.docs_dir.resolve()}")
    logger.info(f"ChromaDB path       : {chroma_path.resolve()}")
    logger.info(f"Collection          : {settings.chroma_collection_name}")
    logger.info(f"Chunk size          : {settings.rag_chunk_size}")
    logger.info(f"Chunk overlap       : {settings.rag_chunk_overlap}")
    logger.info("=" * 60)

    # Load → Split → Embed → Store
    documents = load_documents(args.docs_dir)

    if not documents:
        logger.error("No documents found! Add PDF/DOCX/TXT files to knowledge_base/documents/")
        sys.exit(1)

    chunks = split_documents(
        documents,
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap,
    )

    ingest_to_chroma(
        chunks=chunks,
        chroma_path=chroma_path,
        collection_name=settings.chroma_collection_name,
    )

    logger.info("\n🎉 Ingestion complete! Your knowledge base is ready.")
    logger.info("   Start the server: uv run uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()

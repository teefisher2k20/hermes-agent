"""LlamaIndex + Qdrant Ingestion Pipeline with Document Hashing & Multiprocessing."""

import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from llama_index.core import SimpleDirectoryReader, Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.vector_stores.qdrant import QdrantVectorStore
import qdrant_client

logger = logging.getLogger(__name__)

VAULT_PATH = Path(r"C:\Users\Terrance\Obsidian\Vault")
CACHE_FILE = Path(r"C:\Users\Terrance\Obsidian\.ingestion_cache.json")
QDRANT_DIR = Path(r"C:\Users\Terrance\Obsidian\.qdrant_db")

_QDRANT_CLIENT_CACHE: Optional[qdrant_client.QdrantClient] = None

def compute_file_hash(filepath: Path) -> Optional[str]:
    """Computes SHA-256 hash of a file for incremental indexing. Returns None for empty files."""
    if not filepath.exists() or filepath.stat().st_size == 0:
        return None
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logger.warning(f"Skipping unreadable file {filepath}: {e}")
        return None

def load_doc_hashes() -> Dict[str, str]:
    """Loads previously indexed document hashes."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load hash cache: {e}")
            return {}
    return {}

def save_doc_hashes(hashes: Dict[str, str]) -> None:
    """Saves updated document hashes atomically."""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_cache = CACHE_FILE.with_suffix(".tmp")
    with open(temp_cache, "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=2)
    temp_cache.replace(CACHE_FILE)

def get_qdrant_client() -> qdrant_client.QdrantClient:
    """Returns a cached QdrantClient connected to Docker or persistent disk storage."""
    global _QDRANT_CLIENT_CACHE
    if _QDRANT_CLIENT_CACHE is not None:
        return _QDRANT_CLIENT_CACHE

    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    try:
        client = qdrant_client.QdrantClient(url=qdrant_url, timeout=2.0)
        client.get_collections()
        logger.info(f"Connected to Qdrant Docker container at {qdrant_url}")
        _QDRANT_CLIENT_CACHE = client
        return client
    except Exception:
        logger.info(f"Qdrant Docker at {qdrant_url} unreachable. Using persistent disk storage at {QDRANT_DIR}")
        QDRANT_DIR.mkdir(parents=True, exist_ok=True)
        client = qdrant_client.QdrantClient(path=str(QDRANT_DIR))
        _QDRANT_CLIENT_CACHE = client
        return client

def run_obsidian_ingestion(
    vault_dir: Path = VAULT_PATH,
    num_workers: int = 4,
    force_reindex: bool = False
) -> dict:
    """Executes incremental ingestion pipeline over Obsidian Markdown Vault."""
    if not vault_dir.exists():
        return {
            "status": "error",
            "message": f"Vault path '{vault_dir}' does not exist."
        }

    # 1. Incremental Document Hashing Check
    previous_hashes = load_doc_hashes() if not force_reindex else {}
    current_hashes: Dict[str, str] = {}
    modified_files: List[Path] = []

    for file_path in vault_dir.glob("**/*.md"):
        if file_path.name.startswith(".") or file_path.stat().st_size == 0:
            continue
        rel_path = str(file_path.relative_to(vault_dir))
        file_hash = compute_file_hash(file_path)
        if not file_hash:
            continue

        current_hashes[rel_path] = file_hash
        if previous_hashes.get(rel_path) != file_hash:
            modified_files.append(file_path)

    if not modified_files:
        return {
            "status": "skipped",
            "message": "All Obsidian notes are up to date. Document hashing skipped re-indexing.",
            "total_documents": len(current_hashes),
            "updated_documents": 0,
        }

    # 2. Load modified documents defensively
    reader = SimpleDirectoryReader(
        input_files=[str(p) for p in modified_files],
        required_exts=[".md"],
        errors="ignore",
    )
    documents = reader.load_data()

    if not documents:
        return {
            "status": "skipped",
            "message": "No valid text content extracted from modified files.",
            "total_documents": len(current_hashes),
            "updated_documents": len(modified_files),
        }

    # 3. Setup Qdrant Vector Store
    client = get_qdrant_client()
    vector_store = QdrantVectorStore(client=client, collection_name="obsidian_vault")

    # 4. Ingestion Pipeline Construction
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(chunk_size=512, chunk_overlap=50),
        ],
        vector_store=vector_store,
    )

    # 5. Execute Pipeline with Multiprocessing
    nodes = pipeline.run(documents=documents, num_workers=min(num_workers, len(documents) or 1))

    # 6. Save Updated Hash Cache
    save_doc_hashes(current_hashes)

    return {
        "status": "success",
        "message": f"Successfully ingested {len(modified_files)} updated notes into Qdrant index.",
        "total_documents": len(current_hashes),
        "updated_documents": len(modified_files),
        "nodes_indexed": len(nodes),
    }

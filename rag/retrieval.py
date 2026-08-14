import os
import time
from pathlib import Path
from threading import Lock
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

from backend.services.embedding_service import EmbeddingService

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX")
CACHE_TTL_SECONDS = 300

_cache: dict[tuple[str, int], tuple[float, list[dict]]] = {}
_cache_lock = Lock()


def _cache_key(query: str, top_k: int) -> tuple[str, int]:
    """Return a stable key without changing the semantics of the query."""
    return query, top_k


def clear_retrieval_cache() -> None:
    """Clear cached search results, primarily for tests and index refreshes."""
    with _cache_lock:
        _cache.clear()


def _search_documents(query: str, top_k: int) -> list[dict]:
    """Run the embedding and Azure AI Search calls for a cache miss."""
    client = SearchClient(endpoint=SEARCH_ENDPOINT, index_name=INDEX_NAME, credential=AzureKeyCredential(SEARCH_KEY))

    embedder = EmbeddingService()
    query_vector = embedder.embed_text(query)

    vector_query = VectorizedQuery(vector=query_vector, k_nearest_neighbors=top_k, fields="content_vector")

    results = client.search(
        search_text=None,
        vector_queries=[vector_query],
        select=["content", "filename"]
    )

    return [{"content": r["content"], "filename": r["filename"], "score": r["@search.score"]} for r in results]


def search_documents(query: str, top_k: int = 5) -> list[dict]:
    key = _cache_key(query, top_k)
    now = time.monotonic()

    with _cache_lock:
        cached = _cache.get(key)
        if cached and now - cached[0] < CACHE_TTL_SECONDS:
            # Return a shallow copy so a caller cannot mutate the cache itself.
            return [item.copy() for item in cached[1]]

    documents = _search_documents(query, top_k)

    with _cache_lock:
        _cache[key] = (now, documents)

    return [item.copy() for item in documents]

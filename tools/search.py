import os
import time
import hashlib
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
)

_cache = {}
CACHE_TTL_SECONDS = 300  # 5 minutes


def _cache_key(query: str, top: int) -> str:
    return hashlib.sha256(f"{query}:{top}".encode()).hexdigest()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def _search_with_retry(query: str, top: int):
    return search_client.search(query, top=top)


def search_documents(query: str, top: int = 5) -> dict:
    key = _cache_key(query, top)
    now = time.time()

    if key in _cache:
        cached_result, cached_time = _cache[key]
        if now - cached_time < CACHE_TTL_SECONDS:
            return cached_result

    results = _search_with_retry(query, top)

    context_chunks = []
    sources = []
    for r in results:
        content = r.get("content", "")
        if content:
            context_chunks.append(content)
        source = r.get("filename") or r.get("source")
        if source and source not in sources:
            sources.append(source)

    result = {"context": "\n\n".join(context_chunks), "sources": sources}
    _cache[key] = (result, now)
    return result
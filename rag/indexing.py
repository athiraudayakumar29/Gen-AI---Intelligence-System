import os
import uuid
from pathlib import Path
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchField,
    SearchFieldDataType, VectorSearch, VectorSearchProfile,
    HnswAlgorithmConfiguration
)

from backend.services.embedding_service import EmbeddingService
from rag.chunking import chunk_text

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX")
EMBEDDING_DIMENSIONS = 1536  # text-embedding-3-large; use 1536 if using -small


def get_index_client() -> SearchIndexClient:
    return SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=AzureKeyCredential(SEARCH_KEY))


def get_search_client() -> SearchClient:
    return SearchClient(endpoint=SEARCH_ENDPOINT, index_name=INDEX_NAME, credential=AzureKeyCredential(SEARCH_KEY))


def create_index_if_not_exists():
    index_client = get_index_client()

    existing = [idx.name for idx in index_client.list_indexes()]
    if INDEX_NAME in existing:
        print(f"Index '{INDEX_NAME}' already exists — skipping creation.")
        return

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="filename", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=EMBEDDING_DIMENSIONS,
            vector_search_profile_name="default-vector-profile"
        ),
    ]

    vector_search = VectorSearch(
        profiles=[VectorSearchProfile(name="default-vector-profile", algorithm_configuration_name="default-hnsw")],
        algorithms=[HnswAlgorithmConfiguration(name="default-hnsw")]
    )

    index = SearchIndex(name=INDEX_NAME, fields=fields, vector_search=vector_search)
    index_client.create_index(index)
    print(f"Created index '{INDEX_NAME}'.")


def index_document(text: str, filename: str):
    """
    Chunks a document's text, embeds each chunk, and uploads to Azure AI Search.
    """
    create_index_if_not_exists()

    embedder = EmbeddingService()
    search_client = get_search_client()

    chunks = chunk_text(text)
    if not chunks:
        print(f"No content to index for {filename}")
        return 0

    vectors = embedder.embed_batch(chunks)

    docs = []
    for chunk, vector in zip(chunks, vectors):
        docs.append({
            "id": str(uuid.uuid4()),
            "content": chunk,
            "filename": filename,
            "content_vector": vector
        })

    result = search_client.upload_documents(documents=docs)
    succeeded = sum(1 for r in result if r.succeeded)
    print(f"Indexed {succeeded}/{len(docs)} chunks from {filename}")
    return succeeded
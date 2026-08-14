"""
Combines retrieval (finding relevant chunks) with generation (asking
the LLM to answer using those chunks) — this is the core RAG flow.
"""

from backend.services.llm_service import LLMService
from backend.services.embedding_service import EmbeddingService
from rag.retrieval import search_similar_chunks

llm_service = LLMService()
embedding_service = EmbeddingService()


def answer_with_context(question: str, top_k: int = 3) -> dict:
    # 1. Embed the user's question
    query_vector = embedding_service.embed_text(question)

    # 2. Retrieve the most relevant chunks from Azure AI Search
    chunks = search_similar_chunks(query_vector, top_k=top_k)

    # 3. Build a context block from the retrieved chunks
    if chunks:
        context_text = "\n\n".join(
            f"[Source: {c['filename']}]\n{c['content']}" for c in chunks
        )
    else:
        context_text = "No relevant documents found."

    # 4. Construct the prompt with context + question
    system_prompt = (
        "You are an enterprise knowledge assistant. Answer the user's question "
        "using ONLY the provided context below. If the context doesn't contain "
        "the answer, say you don't have enough information from the available documents."
    )

    user_prompt = f"Context:\n{context_text}\n\nQuestion: {question}"

    reply = llm_service.chat(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    return {
        "reply": reply,
        "sources": [c["filename"] for c in chunks],
        "chunks_used": len(chunks),
    }
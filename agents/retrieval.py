from rag.retrieval import search_documents


def retrieval_node(state: dict) -> dict:
    """
    LangGraph node: takes the user's question from state, searches the
    Azure AI Search index, and writes the retrieved context + sources
    back into state.
    """
    query = state["question"]
    results = search_documents(query, top_k=5)

    context_chunks = [r["content"] for r in results]
    sources = list({r["filename"] for r in results})

    state["context"] = "\n\n".join(context_chunks)
    state["sources"] = sources

    return state
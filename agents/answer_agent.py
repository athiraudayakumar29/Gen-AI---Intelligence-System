from backend.services.llm_service import LLMService

llm = LLMService()

SYSTEM_PROMPT = (
    "You are an enterprise knowledge assistant. Answer the user's question "
    "using ONLY the information in the provided context below. Do not use any "
    "outside knowledge, even if you know the answer. "
    "If the context does not contain the answer, you MUST respond exactly with: "
    "\"I don't have that information in the knowledge base.\" "
    "Do not guess, infer, or supplement with general knowledge under any circumstances. "
    "Be concise and clear when the context does contain the answer."
)


def answer_node(state: dict) -> dict:
    question = state["question"]
    context = state.get("context", "")

    if not context.strip():
        state["answer"] = "I don't have that information in the knowledge base."
        return state

    user_prompt = f"Context:\n{context}\n\nQuestion: {question}"

    llm_result = llm.chat([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ])

    state["answer"] = llm_result["text"]
    state["tokens_used"] = llm_result["tokens_used"]
    return state
from backend.services.rag_service import answer_with_context

result = answer_with_context("How many years of experience?")
print("Reply:", result["reply"])
print("Sources:", result["sources"])
print("Chunks used:", result["chunks_used"])
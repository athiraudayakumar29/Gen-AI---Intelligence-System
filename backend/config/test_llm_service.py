from backend.services.llm_service import LLMService
from backend.services.embedding_service import EmbeddingService

llm = LLMService()
print("Chat test:", llm.simple_ask("Say hello in one sentence."))

embedder = EmbeddingService()
vector = embedder.embed_text("Enterprise AI Knowledge Assistant")
print("Embedding length:", len(vector))
import os
import logging
from openai import OpenAI

logger = logging.getLogger("embedding_service")


def _require_env(*names: str) -> dict:
    values = {name: os.environ.get(name) for name in names}
    missing = [name for name, val in values.items() if not val]
    if missing:
        raise RuntimeError(
            f"EmbeddingService init failed — missing required environment variable(s): {', '.join(missing)}"
        )
    return values


class EmbeddingService:
    def __init__(self):
        env = _require_env("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_KEY", "AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

        self.client = OpenAI(
            base_url=env["AZURE_OPENAI_ENDPOINT"].rstrip("/") + "/",
            api_key=env["AZURE_OPENAI_KEY"],
        )
        self.deployment = env["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]

    def embed_text(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model=self.deployment,
            input=text,
        )
        return response.data[0].embedding

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=self.deployment,
            input=texts,
        )
        return [item.embedding for item in response.data]
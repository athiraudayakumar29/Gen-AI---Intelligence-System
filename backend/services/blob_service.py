import os
from pathlib import Path
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)


class BlobService:
    def __init__(self):
        self.client = BlobServiceClient.from_connection_string(
            os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        )
        self.container_name = os.getenv("AZURE_BLOB_CONTAINER", "documents")
        self._ensure_container()

    def _ensure_container(self):
        container = self.client.get_container_client(self.container_name)
        if not container.exists():
            container.create_container()

    def upload_file(self, filename: str, content: bytes) -> str:
        blob_client = self.client.get_blob_client(container=self.container_name, blob=filename)
        blob_client.upload_blob(content, overwrite=True)
        return blob_client.url
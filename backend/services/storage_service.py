import os
from azure.storage.blob import BlobServiceClient


def _require_env(*names: str) -> dict:
    values = {name: os.environ.get(name) for name in names}
    missing = [name for name, val in values.items() if not val]
    if missing:
        raise RuntimeError(
            f"StorageService init failed — missing required environment variable(s): {', '.join(missing)}"
        )
    return values


class StorageService:
    def __init__(self):
        env = _require_env("AZURE_STORAGE_CONNECTION_STRING", "AZURE_BLOB_CONTAINER")

        self.container_name = env["AZURE_BLOB_CONTAINER"]
        self.blob_service_client = BlobServiceClient.from_connection_string(env["AZURE_STORAGE_CONNECTION_STRING"])
        self.container_client = self.blob_service_client.get_container_client(self.container_name)

    def upload_file(self, filename: str, data: bytes) -> str:
        blob_client = self.container_client.get_blob_client(filename)
        blob_client.upload_blob(data, overwrite=True)
        return blob_client.url

    def download_file_text(self, filename: str) -> str:
        blob_client = self.container_client.get_blob_client(filename)
        data = blob_client.download_blob().readall()
        return data.decode("utf-8", errors="ignore")
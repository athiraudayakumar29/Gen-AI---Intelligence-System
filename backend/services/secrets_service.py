import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


class SecretsService:
    def __init__(self):
        vault_url = os.getenv("KEY_VAULT_URL")
        if not vault_url:
            raise ValueError("KEY_VAULT_URL is not set in environment")
        credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=vault_url, credential=credential)
        self._cache = {}

    def get_secret(self, name: str) -> str:
        if name not in self._cache:
            self._cache[name] = self.client.get_secret(name).value
        return self._cache[name]


_instance = None

def get_secrets_service() -> "SecretsService":
    global _instance
    if _instance is None:
        _instance = SecretsService()
    return _instance
from backend.services.secrets_service import secrets_service

print(secrets_service.get_secret("MCP-INTERNAL-TOKEN"))

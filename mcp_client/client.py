import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from backend.services.secrets_service import get_secrets_service

MCP_TOOLS_URL = os.getenv("MCP_TOOLS_URL", "http://localhost:8080/mcp")  # falls back to local dev


def _secret_or_environment(secret_name: str, *environment_names: str) -> str:
    """Prefer deployment-provided secrets before falling back to Key Vault."""
    for name in environment_names:
        value = os.getenv(name)
        if value:
            return value
    return get_secrets_service().get_secret(secret_name)


def build_mcp_client() -> MultiServerMCPClient:
    github_token = _secret_or_environment("GITHUB-TOKEN", "GITHUB_TOKEN")
    internal_token = _secret_or_environment(
        "MCP-INTERNAL-TOKEN", "MCP_INTERNAL_TOKEN", "MCP-INTERNAL-TOKEN"
    )
    return MultiServerMCPClient({
        "github": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": github_token}
        },
        "internal_tools": {
            "transport": "streamable_http",
            "url": MCP_TOOLS_URL,
            "headers": {"Authorization": f"Bearer {internal_token}"}
        }
    })


async def get_all_tools():
    client = build_mcp_client()
    return await client.get_tools()

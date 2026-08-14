import asyncio
from mcp_client.client import get_all_tools

async def main():
    tools = await get_all_tools()
    print("Available MCP tools:", [t.name for t in tools])

asyncio.run(main())
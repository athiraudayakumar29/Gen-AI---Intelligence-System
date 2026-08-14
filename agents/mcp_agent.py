import asyncio
import logging
from mcp_client.client import get_all_tools

logger = logging.getLogger("mcp_agent")
_tools_cache = None

_mcp_call_counts = {}
MCP_CALL_LIMIT_PER_SESSION = 10

def check_mcp_budget(session_id: str) -> bool:
    count = _mcp_call_counts.get(session_id, 0)
    return count < MCP_CALL_LIMIT_PER_SESSION

def increment_mcp_budget(session_id: str):
    _mcp_call_counts[session_id] = _mcp_call_counts.get(session_id, 0) + 1

async def _get_tools():
    global _tools_cache
    if _tools_cache is None:
        _tools_cache = await get_all_tools()
    return _tools_cache


async def call_mcp_tool_safely(tool, args, timeout=10):
    try:
        return await asyncio.wait_for(tool.ainvoke(args), timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning(f"MCP tool {tool.name} timed out", extra={"tool": tool.name, "args": args})
        return {"error": "timeout"}
    except Exception as e:
        logger.error(f"MCP tool {tool.name} failed: {e}", extra={"tool": tool.name, "args": args})
        return {"error": str(e)}


async def call_mcp_tool(tool_name: str, args: dict, timeout: int = 10) -> dict:
    tools = await _get_tools()
    tool = next((t for t in tools if t.name == tool_name), None)
    if not tool:
        logger.error(f"MCP tool '{tool_name}' not found")
        return {"error": f"Tool '{tool_name}' not found among available MCP tools."}

    result = await call_mcp_tool_safely(tool, args, timeout)
    return {"result": result} if "error" not in result else result


def mcp_node(state: dict) -> dict:
    instruction = state["question"]
    result = asyncio.run(call_mcp_tool(instruction["tool"], instruction.get("args", {})))

    state["answer"] = result.get("result") or result.get("error")
    state["sources"] = [f"MCP: {instruction['tool']}"]
    return state

async def call_mcp_tool(tool_name: str, args: dict, timeout: int = 10) -> dict:
    try:
        tools = await asyncio.wait_for(_get_tools(), timeout=timeout)
        tool = next((t for t in tools if t.name == tool_name), None)
        if not tool:
            return {"error": f"Tool '{tool_name}' not found"}
        result = await asyncio.wait_for(tool.ainvoke(args), timeout=timeout)
        return {"result": result}
    except asyncio.TimeoutError:
        return {"error": f"MCP call to '{tool_name}' timed out after {timeout}s"}
    except Exception as e:
        return {"error": f"MCP call failed: {e}"}
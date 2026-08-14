import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

import asyncio
from agents.planner import create_plan
from agents.mcp_agent import call_mcp_tool


def test_mcp_routing():
    plan = create_plan("Create a GitHub issue titled 'Bug in login flow'")
    agent = plan[0].get("agent") if plan else None
    passed = agent == "mcp"
    print(f"[{'PASS' if passed else 'FAIL'}] MCP routing test — got agent='{agent}', expected 'mcp'")
    return passed


def test_mcp_timeout_handling():
    async def run():
        result = await call_mcp_tool("nonexistent_tool_xyz", {}, timeout=1)
        return result

    result = asyncio.run(run())
    passed = "error" in result
    print(f"[{'PASS' if passed else 'FAIL'}] MCP timeout/failure handling — got: {result}")
    return passed


def test_mcp_auth_failure():
    import httpx
    import os

    url = "http://localhost:8080/mcp"
    try:
        resp = httpx.post(url, json={}, headers={
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }, timeout=5)
        passed = resp.status_code == 401
        print(f"[{'PASS' if passed else 'FAIL'}] MCP auth failure test — got status {resp.status_code}, expected 401")
        return passed
    except Exception as e:
        print(f"[FAIL] MCP auth failure test — request errored instead of returning 401: {e}")
        return False


if __name__ == "__main__":
    results = [
        test_mcp_routing(),
        test_mcp_timeout_handling(),
        test_mcp_auth_failure(),
    ]

    passed = sum(results)
    total = len(results)
    print(f"\nMCP test suite: {passed}/{total} passed")

    if passed < total:
        exit(1)
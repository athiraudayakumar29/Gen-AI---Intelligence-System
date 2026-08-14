# backend/config/test_mcp_auth.py
import httpx
import os

url = "http://localhost:8080/mcp"
token = os.getenv("MCP_INTERNAL_TOKEN")

# Should fail — no token
resp = httpx.post(url, json={}, headers={
    "Accept": "application/json, text/event-stream",
    "Content-Type": "application/json"
})
print("No auth:", resp.status_code)

# Should pass — correct token
resp = httpx.post(url, json={}, headers={
    "Authorization": f"Bearer {token}",
    "Accept": "application/json, text/event-stream",
    "Content-Type": "application/json"
})
print("With auth:", resp.status_code)
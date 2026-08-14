# backend/config/test_mcp_budget.py
from agents.mcp_agent import check_mcp_budget, increment_mcp_budget

session_id = "test-mcp-session"

for i in range(12):
    allowed = check_mcp_budget(session_id)
    print(f"Call {i+1}: allowed={allowed}")
    if allowed:
        increment_mcp_budget(session_id)
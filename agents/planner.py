import json
from backend.services.llm_service import LLMService

llm_service = LLMService()

PLANNER_PROMPT = """You are a routing planner for a multi-agent system. Given a user request, output ONLY a JSON array of steps — no numbering, no prose, no markdown fences, no explanation.

Each step must be a JSON object with:
- "agent": one of "rag", "sql", "report", "email", "mcp"
- "instruction": for rag/sql/report/email, a natural language instruction describing what that agent should do.
  For "mcp", instead provide "tool" (the MCP tool name) and "args" (a JSON object of arguments).

Examples:

Request: "What does the leave policy say about public holidays?"
Output: [{{"agent": "rag", "instruction": "Find information about public holidays in the leave policy"}}]

Request: "Show me total sales for Q1"
Output: [{{"agent": "sql", "instruction": "Query total sales revenue for Q1"}}]

Request: "Compare Q1 and Q2 revenue by region"
Output: [{{"agent": "sql", "instruction": "Query Q1 and Q2 revenue broken down by region"}}]

Request: "Generate a report on Q1 and Q2 sales performance by region"
Output: [{{"agent": "sql", "instruction": "Query Q1 and Q2 sales by region"}}, {{"agent": "report", "instruction": "Generate a performance report from the sales data by region"}}]

Request: "Create a GitHub issue titled 'Bug in login flow'"
Output: [{{"agent": "mcp", "tool": "create_github_issue", "args": {{"title": "Bug in login flow"}}}}]

Now respond with ONLY the JSON array for this request, nothing else:

Request: "{request}"
Output:"""


def create_plan(request: str) -> list[dict]:
    raw = llm_service.simple_ask(PLANNER_PROMPT.format(request=request))
    raw = raw.strip()

    # strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        raw = raw.replace("json", "", 1).strip()

    try:
        plan = json.loads(raw)
        if not isinstance(plan, list):
            raise ValueError("Plan is not a list")
        return plan
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[planner] JSON parse failed: {e}")
        print(f"[planner] Raw LLM output was:\n{raw!r}\n")
        return [{"agent": "rag", "instruction": request}]
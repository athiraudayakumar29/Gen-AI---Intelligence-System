import os
from mcp.server.fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from tools.sql import run_sql_query
from tools.search import search_documents
from tools.pdf import generate_pdf_report
from agents.sql_agent import generate_sql, is_safe_query

# Support the original .env spelling while using the conventional underscore
# name for container and deployment environments.
MCP_AUTH_TOKEN = os.getenv("MCP_INTERNAL_TOKEN") or os.getenv("MCP-INTERNAL-TOKEN")

mcp = FastMCP("enterprise-agent-tools")


class BearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        auth_header = request.headers.get("Authorization", "")
        if auth_header != f"Bearer {MCP_AUTH_TOKEN}":
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        return await call_next(request)


@mcp.tool()
def query_sales(question: str) -> dict:
    """Answer a natural language question about sales data by generating and running a safe SQL query."""
    sql = generate_sql(question)
    if not is_safe_query(sql):
        return {"error": "Generated query failed safety validation."}
    rows = run_sql_query(sql)
    return {"sql": sql, "results": rows}


@mcp.tool()
def search_knowledge_base(query: str) -> dict:
    """Search internal documents (policies, reports) for relevant context."""
    return search_documents(query)


@mcp.tool()
def create_pdf_report(title: str, content: str) -> str:
    """Generate a PDF report and return a confirmation with byte size."""
    pdf_bytes = generate_pdf_report(title, content)
    return f"Generated PDF report '{title}', {len(pdf_bytes)} bytes."


if __name__ == "__main__":
    app = mcp.streamable_http_app()
    app.add_middleware(BearerAuthMiddleware)

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

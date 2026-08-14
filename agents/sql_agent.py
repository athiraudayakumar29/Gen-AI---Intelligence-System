import sqlite3
import re
from pathlib import Path
from backend.services.llm_service import LLMService

llm_service = LLMService()

DB_PATH = Path(__file__).resolve().parents[1] / "enterprise-documents" / "db" / "sales.db"

SCHEMA_DESCRIPTION = """
Table: sales
Columns:
  - id (INTEGER)
  - quarter (TEXT) — e.g. 'Q1', 'Q2'
  - region (TEXT) — e.g. 'North America', 'Europe'
  - product (TEXT) — e.g. 'Widget A', 'Widget B'
  - revenue (REAL)
"""

SQL_PROMPT = """You are a SQL generator for a SQLite database. Given the schema and a natural language question, write a single SELECT query that answers it.

Rules:
- ONLY output the raw SQL query, nothing else. No markdown, no explanation.
- ONLY use SELECT statements. Never use INSERT, UPDATE, DELETE, DROP, ALTER, or any write operation.
- Only reference the table and columns described below.

Schema:
{schema}

Question: {question}

SQL:
"""

# Safety: block any query that isn't a plain SELECT
FORBIDDEN_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|TRUNCATE|ATTACH|PRAGMA)\b",
    re.IGNORECASE
)


def generate_sql(question: str) -> str:
    prompt = SQL_PROMPT.format(schema=SCHEMA_DESCRIPTION, question=question)
    raw = llm_service.simple_ask(prompt).strip()
    # Strip markdown fences if the model adds them despite instructions
    raw = re.sub(r"^```sql\s*|```$", "", raw, flags=re.IGNORECASE | re.MULTILINE).strip()
    return raw


def is_safe_query(sql: str) -> bool:
    if not sql.strip().upper().startswith("SELECT"):
        return False
    if FORBIDDEN_KEYWORDS.search(sql):
        return False
    if ";" in sql.strip()[:-1]:  # no stacked statements
        return False
    return True


def execute_query(sql: str, max_rows: int = 100) -> list[dict]:
    conn = sqlite3.connect(DB_PATH, timeout=5)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = [dict(row) for i, row in enumerate(cursor.fetchall()) if i < max_rows]
    conn.close()
    return rows


def sql_node(state: dict) -> dict:
    question = state["question"]
    sql = generate_sql(question)

    if not is_safe_query(sql):
        state["answer"] = "I couldn't safely execute that query — it may involve an unsupported or unsafe operation."
        state["sources"] = []
        return state

    try:
        rows = execute_query(sql)
    except Exception as e:
        state["answer"] = f"The query failed to execute: {e}"
        state["sources"] = []
        return state

    if not rows:
        state["answer"] = "The query ran successfully but returned no results."
    else:
        summary_prompt = f"""Given this question: "{question}"
And this query result: {rows}

Write a concise, natural-language answer (1-3 sentences)."""
        state["answer"] = llm_service.simple_ask(summary_prompt)

    state["sources"] = [f"SQL: {sql}"]
    return state
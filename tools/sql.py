import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "enterprise-documents" / "db" / "sales.db"


def run_sql_query(sql: str) -> list[dict]:
    """
    Executes a read-only SQL query against the sales database and returns rows as dicts.
    Caller is responsible for validating the query is safe before calling this.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows
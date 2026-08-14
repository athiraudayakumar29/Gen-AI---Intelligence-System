import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parents[2] / "enterprise-documents" / "db" / "sales.db"
db_path.parent.mkdir(parents=True, exist_ok=True)


conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY,
    quarter TEXT,
    region TEXT,
    product TEXT,
    revenue REAL
)
""")

sample_data = [
    ("Q1", "North America", "Widget A", 125000),
    ("Q1", "Europe", "Widget A", 98000),
    ("Q1", "North America", "Widget B", 76000),
    ("Q2", "North America", "Widget A", 142000),
    ("Q2", "Europe", "Widget A", 105000),
    ("Q2", "North America", "Widget B", 81000),
]

cursor.execute("DELETE FROM sales")
cursor.executemany(
    "INSERT INTO sales (quarter, region, product, revenue) VALUES (?, ?, ?, ?)",
    sample_data
)

conn.commit()
conn.close()
print(f"Seeded database at {db_path}")
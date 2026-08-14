# backend/config/test_tools.py
from tools.sql import run_sql_query
from tools.search import search_documents
from tools.pdf import generate_pdf_report
from tools.email import send_email

print("SQL tool:", run_sql_query("SELECT * FROM sales WHERE quarter = 'Q1'"))
print("Search tool:", search_documents("leave policy")["sources"])

pdf_bytes = generate_pdf_report("Test Report", "This is a test report.\nSecond line of content.")
with open("test_report.pdf", "wb") as f:
    f.write(pdf_bytes)
print("PDF tool: wrote test_report.pdf,", len(pdf_bytes), "bytes")

print("Email tool:", send_email("test@example.com", "Test Subject", "Test body"))
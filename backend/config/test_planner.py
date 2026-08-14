# backend/config/test_planner.py
from agents.graph import run_agent

result = run_agent("Compare Q1 and Q2 sales and email a summary to the team")
print("ANSWER:\n", result["answer"])
print("\nSOURCES:", result["sources"])
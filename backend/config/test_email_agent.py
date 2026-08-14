from agents.graph import run_agent

result = run_agent("Get our sales data, summarize it, and email it to my manager")

print("PLAN:", result["plan"])
print("\n--- FULL ANSWER (all steps) ---")
print(result["answer"])
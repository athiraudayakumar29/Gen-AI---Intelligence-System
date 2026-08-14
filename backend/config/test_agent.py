from agents.graph import run_agent

result = run_agent("How many years of experience?")
print("ANSWER:", result["answer"])
print("SOURCES:", result["sources"])
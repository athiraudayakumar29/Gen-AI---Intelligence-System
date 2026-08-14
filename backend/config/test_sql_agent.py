from agents.graph import run_agent

test_questions = [
    "What were our total sales in Q2 2026?",
    "Who has the most years of experience?",
    "Get our sales data, summarize it, and email it to my manager",
]

for q in test_questions:
    result = run_agent(q)
    print(f"\nQUESTION: {q}")
    print(f"PLAN: {result['plan']}")
    print(f"ANSWER: {result['answer']}")
from agents.graph import run_agent

test_questions = [
    "How many years of experience does she have?",       # → retrieval
    "What were our total sales last quarter?",             # → sql
    "Draft an email to my manager about the leave policy", # → email
]

for q in test_questions:
    result = run_agent(q)
    print(f"\nQUESTION: {q}")
    print(f"ROUTE: {result['route']}")
    print(f"ANSWER: {result['answer']}")
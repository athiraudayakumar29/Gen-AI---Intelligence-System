import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from agents.graph import run_agent
from agents.planner import create_plan


def load_dataset(path: str) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def score_retrieval_relevance(answer: str, expected_keywords: list[str]) -> float:
    if not expected_keywords:
        return 1.0
    answer_lower = answer.lower()
    hits = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
    return hits / len(expected_keywords)


def score_source_match(actual_sources: list[str], expected_sources: list[str]) -> float:
    if not expected_sources:
        return 1.0
    hits = sum(1 for src in expected_sources if any(src in s for s in actual_sources))
    return hits / len(expected_sources)


def check_no_hallucination(answer: str) -> bool:
    hedge_phrases = ["don't have", "couldn't find", "no relevant information", "not available"]
    return any(phrase in answer.lower() for phrase in hedge_phrases)


def run_planner_routing_test(question: str, expected_category: str) -> bool:
    plan = create_plan(question)
    if not plan:
        return False
    agents_in_plan = [step.get("agent") for step in plan]
    return expected_category in agents_in_plan


def evaluate(dataset_path: str) -> dict:
    dataset = load_dataset(dataset_path)
    results = []

    for item in dataset:
        question = item["question"]
        category = item["category"]

        routing_correct = run_planner_routing_test(question, category)

        result = run_agent(question)
        answer = result.get("answer", "")
        sources = result.get("sources", [])

        if item.get("expect_no_answer"):
            passed = check_no_hallucination(answer)
            relevance_score = 1.0 if passed else 0.0
        else:
            relevance_score = score_retrieval_relevance(answer, item.get("expected_keywords", []))
            passed = relevance_score >= 0.5

        source_score = score_source_match(sources, item.get("expected_sources", []))

        results.append({
            "id": item["id"],
            "question": question,
            "category": category,
            "routing_correct": routing_correct,
            "relevance_score": relevance_score,
            "source_score": source_score,
            "passed": passed and routing_correct
        })

    total = len(results)
    passed_count = sum(1 for r in results if r["passed"])
    avg_relevance = sum(r["relevance_score"] for r in results) / total
    avg_routing_accuracy = sum(1 for r in results if r["routing_correct"]) / total

    return {
        "total": total,
        "passed": passed_count,
        "pass_rate": passed_count / total,
        "avg_relevance_score": avg_relevance,
        "routing_accuracy": avg_routing_accuracy,
        "results": results
    }


if __name__ == "__main__":
    dataset_path = Path(__file__).resolve().parent / "datasets" / "qa_pairs.json"
    report = evaluate(str(dataset_path))

    print(f"\n{'='*50}")
    print(f"EVALUATION REPORT")
    print(f"{'='*50}")
    print(f"Total tests: {report['total']}")
    print(f"Passed: {report['passed']} ({report['pass_rate']*100:.1f}%)")
    print(f"Avg relevance score: {report['avg_relevance_score']:.2f}")
    print(f"Routing accuracy: {report['routing_accuracy']*100:.1f}%")
    print(f"\nDetailed results:")
    for r in report["results"]:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"  [{status}] {r['id']} ({r['category']}) - relevance: {r['relevance_score']:.2f}, routing: {r['routing_correct']}")

    if report["pass_rate"] < 0.8:
        print(f"\nWARNING: Pass rate below 80% threshold — review before deploying.")
        sys.exit(1)
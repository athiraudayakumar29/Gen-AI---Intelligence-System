
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from agents.answer_agent import answer_node
from agents.planner import create_plan
from agents.retrieval import retrieval_node
from agents.mcp_agent import mcp_node


class AgentState(TypedDict):
    message: str
    question: Optional[str]
    intent: Optional[str]
    answer: Optional[str]
    sources: Optional[list[str]]
    report_pdf: Optional[bytes]
    pending_email: Optional[dict]
    plan: Optional[list[dict]]
    plan_results: Optional[list[str]]


AGENT_MAP = {
    "rag": lambda q: run_rag_step(q),
    "sql": lambda q: run_sql_step(q),
    "report": lambda q: run_report_step(q),
    "email": lambda q: run_email_step(q),
    "mcp": lambda step: run_mcp_step(step),  # note: mcp needs the full step dict, not just instruction
}

def run_mcp_step(step: dict) -> tuple[str, list[str]]:
    result = mcp_node({"question": step})
    return result["answer"], result.get("sources", [])

def run_rag_step(question: str) -> tuple[str, list[str]]:
    result = retrieval_node({"message": question, "question": question})
    result = answer_node(result)
    return result["answer"], result.get("sources", [])


def run_sql_step(question: str) -> tuple[str, list[str]]:
    from agents.sql_agent import sql_node
    result = sql_node({"question": question})
    return result["answer"], result.get("sources", [])


def run_report_step(question: str) -> tuple[str, list[str]]:
    from agents.report_agent import report_node
    result = report_node({"question": question})
    return result["answer"], result.get("sources", [])


def run_email_step(question: str) -> tuple[str, list[str]]:
    from agents.email_agent import email_node
    result = email_node({"question": question})
    return result["answer"], result.get("sources", [])


def planner_node(state: AgentState) -> AgentState:
    plan = create_plan(state["message"])
    state["plan"] = plan
    state["plan_results"] = []
    return state


def execute_plan_node(state: AgentState) -> AgentState:
    plan = state["plan"]
    results = []
    all_sources = []
    previous_result = ""

    for step in plan:
        agent = step.get("agent", "rag")
        handler = AGENT_MAP.get(agent, AGENT_MAP["rag"])

        if agent == "mcp":
            answer, sources = handler(step)
        else:
            instruction = step.get("instruction", "").replace("{previous_result}", previous_result)
            answer, sources = handler(instruction)

        results.append(f"[{agent}] {answer}")
        all_sources.extend(sources)
        previous_result = answer

    state["plan_results"] = results
    state["answer"] = "\n\n".join(results)
    state["sources"] = all_sources
    return state


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("execute_plan", execute_plan_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "execute_plan")
    graph.add_edge("execute_plan", END)

    return graph.compile()


compiled_graph = build_graph()


def run_agent(message: str) -> dict:
    result = compiled_graph.invoke({
        "message": message,
        "question": message,
        "intent": None,
        "answer": None,
        "sources": None,
        "report_pdf": None,
        "pending_email": None,
        "plan": None,
        "plan_results": None
    })
    return {"answer": result["answer"], "sources": result.get("sources", [])}
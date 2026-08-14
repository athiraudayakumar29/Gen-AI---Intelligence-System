from backend.services.llm_service import LLMService
from tools.search import search_documents
from tools.sql import run_sql_query
from tools.pdf import generate_pdf_report
from agents.sql_agent import generate_sql, is_safe_query

llm_service = LLMService()

REPORT_SYNTHESIS_PROMPT = """You are writing a business report based on the following gathered information.

Document context (from internal knowledge base):
{doc_context}

Structured data results:
{sql_results}

User's report request: {question}

Write a clear, well-organized report (use short sections with headers) that directly addresses the request, using only the information provided above. If some requested information isn't available in either source, say so plainly rather than inventing it.
"""


def gather_report_inputs(question: str) -> dict:
    # Pull relevant document context
    search_result = search_documents(question)

    # Attempt a SQL query if the question implies structured data
    sql_results = []
    sql_query = None
    try:
        sql_query = generate_sql(question)
        if is_safe_query(sql_query):
            sql_results = run_sql_query(sql_query)
    except Exception:
        sql_results = []

    return {
        "doc_context": search_result["context"] or "No relevant documents found.",
        "doc_sources": search_result["sources"],
        "sql_results": sql_results if sql_results else "No structured data results.",
        "sql_query": sql_query
    }


def report_node(state: dict) -> dict:
    question = state["question"]
    inputs = gather_report_inputs(question)

    prompt = REPORT_SYNTHESIS_PROMPT.format(
        doc_context=inputs["doc_context"],
        sql_results=inputs["sql_results"],
        question=question
    )
    report_text = llm_service.simple_ask(prompt)

    # Generate a downloadable PDF version
    pdf_bytes = generate_pdf_report(title="Generated Report", content=report_text)

    state["answer"] = report_text
    state["sources"] = inputs["doc_sources"] + ([f"SQL: {inputs['sql_query']}"] if inputs["sql_query"] else [])
    state["report_pdf"] = pdf_bytes  # available if the API layer wants to offer a download
    return state
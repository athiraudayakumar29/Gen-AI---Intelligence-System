import re
from backend.services.llm_service import LLMService
from tools.email import send_email

llm_service = LLMService()

DRAFT_PROMPT = """You are drafting an email based on this request: "{request}"

Extract or infer:
- recipient email address (if not given, use "team@example.com" as a placeholder)
- a concise subject line
- a clear, professional body

Respond in exactly this format, nothing else:
TO: <email>
SUBJECT: <subject>
BODY:
<body text>
"""


def draft_email(request: str) -> dict:
    raw = llm_service.simple_ask(DRAFT_PROMPT.format(request=request))

    to_match = re.search(r"TO:\s*(.+)", raw)
    subject_match = re.search(r"SUBJECT:\s*(.+)", raw)
    body_match = re.search(r"BODY:\s*\n(.+)", raw, re.DOTALL)

    return {
        "to": to_match.group(1).strip() if to_match else "team@example.com",
        "subject": subject_match.group(1).strip() if subject_match else "Update",
        "body": body_match.group(1).strip() if body_match else raw
    }


def email_node(state: dict) -> dict:
    """
    Drafts the email and pauses for human approval — does NOT send automatically.
    The API layer surfaces the draft to the user; a separate /email/confirm
    endpoint calls send_email() only after explicit approval.
    """
    question = state["question"]
    draft = draft_email(question)

    state["answer"] = (
        f"Draft ready for review:\n\n"
        f"To: {draft['to']}\n"
        f"Subject: {draft['subject']}\n\n"
        f"{draft['body']}\n\n"
        f"(Not sent — awaiting confirmation.)"
    )
    state["sources"] = []
    state["pending_email"] = draft  # picked up by the confirm endpoint
    return state
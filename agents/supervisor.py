from backend.services.llm_service import LLMService

llm_service = LLMService()

ROUTING_PROMPT = """You are a routing classifier for an enterprise AI assistant.
Classify the user's message into exactly one category:

- "rag" — general questions, document lookups, "what does X say", summaries of uploaded docs
- "sql" — questions about structured/tabular data, sales figures, database records, "how many", "show me records"
- "report" — requests to generate a report or structured summary document
- "email" — requests to send, draft, or email something to someone

Respond with ONLY the category word, nothing else.

User message: {message}
"""


def classify_intent(message: str) -> str:
    prompt = ROUTING_PROMPT.format(message=message)
    result = llm_service.simple_ask(prompt).strip().lower()

    valid = {"rag", "sql", "report", "email"}
    if result not in valid:
        return "rag"  # safe default
    return result
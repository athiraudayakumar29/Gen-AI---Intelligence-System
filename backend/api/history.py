from fastapi import APIRouter, Depends
from memory.cosmos import ConversationMemory
from backend.api.deps import get_current_user

router = APIRouter()
memory = ConversationMemory()


@router.get("")
def get_history(session_id: str, user_id: str = Depends(get_current_user)):
    """
    Returns the conversation history for a given session_id, scoped to the
    authenticated user. A user cannot retrieve another user's messages even
    if they know or guess a session_id that isn't theirs.
    """
    messages = memory.get_history(session_id, user_id)
    return {
        "session_id": session_id,
        "messages": messages
    }
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.api.deps import get_current_user
from memory.cosmos import ConversationMemory

router = APIRouter()
memory = ConversationMemory()


class FeedbackRequest(BaseModel):
    session_id: str
    message_id: str
    rating: str  # "up" or "down"


@router.post("")
def submit_feedback(request: FeedbackRequest, user_id: str = Depends(get_current_user)):
    memory.container.create_item(body={
        "id": f"feedback-{request.message_id}",
        "session_id": request.session_id,
        "type": "feedback",
        "message_id": request.message_id,
        "rating": request.rating,
        "user_id": user_id
    })
    return {"status": "recorded"}
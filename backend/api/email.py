from fastapi import APIRouter
from pydantic import BaseModel
from tools.email import send_email

router = APIRouter()


class EmailConfirmRequest(BaseModel):
    to: str
    subject: str
    body: str


@router.post("/confirm")
def confirm_email(request: EmailConfirmRequest):
    result = send_email(request.to, request.subject, request.body)
    return result
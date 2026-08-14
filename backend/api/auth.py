from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.user_service import user_service
from backend.services.auth_service import create_access_token

router = APIRouter()


class SignupRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/signup")
def signup(request: SignupRequest):
    existing = user_service.get_user_by_email(request.email)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    user = user_service.create_user(request.email, request.password)
    token = create_access_token(user["user_id"])
    return {"access_token": token, "token_type": "bearer", "user_id": user["user_id"]}


@router.post("/login")
def login(request: LoginRequest):
    user = user_service.authenticate(request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user["user_id"])
    return {"access_token": token, "token_type": "bearer", "user_id": user["user_id"]}
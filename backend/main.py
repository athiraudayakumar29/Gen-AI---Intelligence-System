import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import chat, upload, history, feedback
from backend.api import email
from backend.api import auth

from backend.config.logging_config import setup_logging
from backend.config.rate_limiter import limiter
from backend.middleware.request_id import RequestIDMiddleware

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

print(">>> BACKEND MAIN.PY LOADED - VERSION MARKER XYZ123 <<<")

setup_logging()

from azure.monitor.opentelemetry import configure_azure_monitor

if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    configure_azure_monitor(connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"))

app = FastAPI(title="Enterprise AI Knowledge Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://thankful-bay-075c3f10f.7.azurestaticapps.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(history.router, prefix="/history", tags=["History"])
app.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
app.include_router(email.router, prefix="/email", tags=["Email"])
app.add_middleware(RequestIDMiddleware)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
def root():
    return {"status": "Enterprise AI Agent backend is running"}
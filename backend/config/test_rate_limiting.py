# backend/config/test_rate_limiting.py
from backend.services.usage_service import usage_service

usage_service.log_usage("test-session", "test-user", 150)
usage_service.log_usage("test-session", "test-user", 200)

total = usage_service.get_session_total("test-session")
print(f"Total tokens for session: {total}")
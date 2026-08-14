# backend/config/test_logging.py
import logging
from backend.config.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("test")

logger.info("test log line", extra={"trace_id": "test-123", "custom_field": "value"})
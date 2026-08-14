import uuid
import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("request_tracing")


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        trace_id = str(uuid.uuid4())
        request.state.trace_id = trace_id
        start_time = time.time()

        logger.info(
            "request_started",
            extra={"trace_id": trace_id, "path": request.url.path, "method": request.method}
        )

        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(
                "request_failed",
                extra={"trace_id": trace_id, "path": request.url.path, "error": str(e)}
            )
            raise

        duration_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(
            "request_completed",
            extra={"trace_id": trace_id, "path": request.url.path, "status_code": response.status_code, "duration_ms": duration_ms}
        )

        response.headers["X-Trace-ID"] = trace_id
        return response
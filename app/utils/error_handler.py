import logging
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Set up a logger for error handling
logger = logging.getLogger("app.error")

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            # Process the request normally
            response = await call_next(request)
            return response
        except Exception as e:
            # Log error details to file and console
            error_trace = traceback.format_exc()
            logger.error(f"Error while handling request {request.url.path}: {e}\n{error_trace}")

            # Return clean JSON response to the user
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error", "error": str(e)},
            )

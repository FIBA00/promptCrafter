import sys
import os

# Add the directory containing this file to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from utility.logger import get_logger
from routers import process_prompt, user
import traceback
from prometheus_fastapi_instrumentator import Instrumentator


lg = get_logger(__file__)
version = "0.1.0"

app = FastAPI(
    title="PromptCrafter Backend API",
    description="API for processing and structuring prompts.",
    version=version,
)

# --- Global Exception Handling ---


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catches any unhandled exception, logs the full stack trace, and returns
    a detailed JSON error response.

    CRITICAL: This prevents random 500 "Internal Server Error" white screens
    and ensures we always know exactly what failed in the logs.
    """
    # Capture the full traceback as a string
    error_details = traceback.format_exc()

    # Log it with our custom logger
    lg.error(f"Global Exception Caught:\n{error_details}")

    # Return a structured error to the client (Helpful for debugging)
    # in PROD, you might want to hide the 'traceback' field.
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An unexpected internal server error occurred.",
            "detail": str(exc),
            "path": request.url.path,
            "method": request.method,
            # "traceback": error_details # Uncomment if you want full stack trace in response
        },
    )


def metrics_app():
    """Creates a separate FastAPI app for the /metrics endpoint."""
    app = FastAPI()
    Instrumentator().expose(app)
    return app


app.include_router(process_prompt.router, prefix="/api/v1", tags=["process"])
app.include_router(user.router, prefix="/api/v1", tags=["process"])

# Use absolute path for static files to work in both Docker and local envs
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/home", StaticFiles(directory=static_dir, html=True), name="frontend")

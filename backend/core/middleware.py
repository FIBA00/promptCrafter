import time
import logging

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from utility.logger import get_logger


# to disable the uvicorn logs
logger = logging.getLogger("uvicorn.access")
logger.disabled = True

lg = get_logger(__file__)


def register_middleware(app: FastAPI):
    # NOTE: custom logging for monitoring the performance, we can disable it later if need be.
    @app.middleware("http")
    def custom_logging(request: Request, call_next):
        start_time = time.time()
        response = call_next(request)
        processing_time = time.time() - start_time
        message = f"{request.method} - {request.url.path} - {response.status_code} - completed after {processing_time} seconds."
        lg.info(message)
        return response

    # our middle wares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "testserver"]
    )

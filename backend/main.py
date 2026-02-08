"""
RESTful Prompt restructing app


"""

import os
import sys
from typing import Any

# Add the directory containing this file to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import prompt, user
from core.config import settings
from core.middleware import register_middleware
from core.custom_error_handlers import register_all_errors
from prometheus_fastapi_instrumentator import Instrumentator

from utility.logger import get_logger

lg = get_logger(script_path=__file__)
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
REDIS_URL = settings.REDIS_URL
STATIC_FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# our app
description = """
A RESTful API for a AI prompt restructing system.

## Prompts
* You can **create**, **read**, **update**, and **delete** prompts.

## Users
* **Create** and **Login** users (JWT Auth).
* **Password Reset** and **Email Verification**.

"""
version = settings.VERSION

tags_metadata = [
    {
        "name": "prompts",
        "description": "Operations with prompts. The **CORE** logic of the app.",
    },
    {
        "name": "user",
        "description": "Manages reviews added to books.",
    },
]

app = FastAPI(
    title="PromptCrafter Backend API",
    description=description,
    version=settings.VERSION or version,
    contact={
        "name": "Fraol Bulti",
        "url": "https://github.com/FIBA00",
        "email": "fraolbulti0@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=tags_metadata,
    openapi_url=f"/api/{settings.VERSION or version}/openapi.json",
    docs_url=f"/api/{settings.VERSION or version}/docs",
    redoc_url=f"/api/{settings.VERSION or version}/redoc",
)


# --- Global Exception Handling ---


def metrics_app() -> Any:
    """Creates a separate FastAPI app for the /metrics endpoint."""
    app = FastAPI(prefix="/metrics", title="Metrics App")
    Instrumentator().expose(app)
    return app


register_all_errors(app=app)
register_middleware(app)
app.include_router(
    router=prompt.router, prefix=f"/api/{settings.VERSION or version}", tags=["prompts"]
)
app.include_router(
    router=user.router, prefix=f"/api/{settings.VERSION or version}", tags=["user"]
)


app.mount(
    path=f"/api/{settings.VERSION or version}/home",
    app=StaticFiles(directory=STATIC_FRONTEND_DIR, html=True),
    name="frontend",
)
# app.mount(path=f"/api/{settings.VERSION or version}/admin", app=admin_app, name="admin")

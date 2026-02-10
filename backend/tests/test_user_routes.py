from fastapi import status
from core.config import settings

PREFIX = f"/api/{settings.VERSION or "v1.1"}/user"

# Tests for password login/signup removed as we moved to Google Auth only.
# TODO: Add tests for Google Auth (mocked) and other existing routes like /refresh, /logout

"""
Custom Error Handling Module:
instead of repeating the same line we use this module to handle our errors,


"""

from typing import Callable
from fastapi import status, FastAPI
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from utility.logger import get_logger
import traceback

lg = get_logger(script_path=__file__)


class PromptCrafterException(Exception):
    """
    Base Exception for PromptCrafter application."""

    pass


class PromptNotModified(PromptCrafterException):
    """
    Exception raised when a prompt modification request does not result in any changes."""

    pass


class PromptsNotFoundForCurrentUser(PromptCrafterException):
    """
    Exception raised when no prompts are found for the current user."""

    pass


class InvalidToken(PromptCrafterException):
    """
    Exception raised when an invalid token is provided."""

    pass


class RevokedToken(PromptCrafterException):
    """
    Exception raised when a revoked token is provided."""

    pass


class AccssTokenRequired(PromptCrafterException):
    """
    Exception raised when an access token is required but missing."""

    pass


class RefreshTokenRequired(PromptCrafterException):
    """
    Exception raised when a refresh token is required but missing."""

    pass


class UserAlreadyExists(PromptCrafterException):
    """
    Exception raised when attempting to create a user that already exists."""

    pass


class InvalidCredentials(PromptCrafterException):
    """
    Exception raised when invalid credentials (email or password) are provided."""

    pass


class PromptNotFound(PromptCrafterException):
    """
    Exception raised when a requested prompt is not found."""

    pass


class UserNotFound(PromptCrafterException):
    """
    Exception raised when a requested user is not found."""

    pass


class InsufficientPermissions(PromptCrafterException):
    """
    Exception raised when a user lacks the necessary permissions."""

    pass


class TagNotFound(PromptCrafterException):
    """
    Exception raised when a requested tag is not found."""

    pass


class AccountNotVerified(PromptCrafterException):
    """
    Exception raised when a user account is not verified
    """

    pass


class RateLimitExceeded(PromptCrafterException):
    """
    Exception raised when a user exceeds their daily token limit."""

    pass


def create_exception_handler(
    status_code: int, initial_detail: any
) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: PromptCrafterException):
        return JSONResponse(
            status_code=status_code,
            content={"detail": initial_detail},
        )

    return exception_handler


def register_all_errors(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "User already exists.",
                "error_code": "user_exists",
                "resolution": "If this is your account, please log in. Otherwise, use a different email to register.",
            },
        ),
    )

    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid Credentials.",
                "error_code": "invalid_credentials",
                "resolution": "Double-check your email and password and try again.",
            },
        ),
    )

    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid or expired.",
                "error_code": "invalid_token",
                "resolution": "Please log in again to obtain a new token.",
            },
        ),
    )

    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token has been revoked.",
                "error_code": "revoked_token",
                "resolution": "Please log in again to obtain a new token.",
            },
        ),
    )

    app.add_exception_handler(
        AccssTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Access Token Required.",
                "error_code": "access_token_required",
                "resolution": "Please provide a valid access token in the Authorization header.",
            },
        ),
    )

    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Refresh Token Required.",
                "error_code": "refresh_token_required",
                "resolution": "Please provide a valid refresh token to generate a new access token.",
            },
        ),
    )

    app.add_exception_handler(
        InsufficientPermissions,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Insufficient Permissions.",
                "error_code": "insufficient_permissions",
                "resolution": "You do not have the necessary permissions to perform this action. Contact support if you believe this is an error.",
            },
        ),
    )

    app.add_exception_handler(
        PromptNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Prompt Not Found.",
                "error_code": "prompt_not_found",
                "resolution": "Verify the prompt UID and try again.",
            },
        ),
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User Not Found.",
                "error_code": "user_not_found",
                "resolution": "Verify the user ID and try again.",
            },
        ),
    )

    app.add_exception_handler(
        TagNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Tag Not Found.",
                "error_code": "tag_not_found",
                "resolution": "Verify the tag and try again.",
            },
        ),
    )
    app.add_exception_handler(
        AccountNotVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Account not verified.",
                "error_code": "account_not_verified",
                "resolution": "Verify your account by requesting verify email.",
            },
        ),
    )

    app.add_exception_handler(
        RateLimitExceeded,
        create_exception_handler(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            initial_detail={
                "message": "Daily token limit exceeded.",
                "error_code": "rate_limit_exceeded",
                "resolution": "You have used all your AI tokens for today. Quota resets daily.",
            },
        ),
    )
    app.add_exception_handler(
        PromptNotModified,
        create_exception_handler(
            status_code=status.HTTP_304_NOT_MODIFIED,
            initial_detail={
                "message": "Prompt not modified.",
                "error_code": "prompt_not_modified",
                "resolution": "The prompt was not modified because the prompt has missing 'role' . Please make changes to the prompt data and try again.",
            },
        ),
    )

    app.add_exception_handler(
        PromptsNotFoundForCurrentUser,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "No prompts found for the current user.",
                "error_code": "prompts_not_found_for_user",
                "resolution": "No prompts were found for the current user. If you haven't created any prompts yet, start by creating a new prompt. If you believe this is an error, please contact support for assistance.",
            },
        ),
    )

    app.add_exception_handler(Exception, global_exception_handler)

    @app.exception_handler(500)
    async def internal_server_error(request, exc):
        return JSONResponse(
            content={
                "message": "Internal Server Error.",
                "error_code": "internal_server_error",
                "resolution": "An unexpected error occurred. Please try again later or contact support if the issue persists.",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


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

# user page
from datetime import timedelta, datetime
from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

# our custom module imports
from db.database import get_db
from db.redis import (
    add_jit_to_blocklist,
    increment_login_attempts,
    get_login_attempts,
    reset_login_attempts,
)
from core.config import settings
from core.celery_tasks import send_email
from core.custom_error_handlers import InvalidCredentials, InvalidToken
from core.schemas import (
    UserCreateSchema,
    UserOutSchema,
    TokenOutSchema,
    EmailModel,
    UserSignupResponse,
    PasswordResetRequestSchema,
    PasswordResetSchema,
)
from auth.oauth2 import (
    verify_password,
    create_access_token,
    decode_access_token,
    create_url_safe_token,
    decode_url_safe_token,
    hash_password,
)

from auth.dependencies import get_refresh_token, get_access_token
from core.custom_error_handlers import UserNotFound
from utility.logger import get_logger
from services.user_service import UserService


router = APIRouter(prefix="/user", tags=["user"])
# router.mount("/static", StaticFiles(directory="static"), name="static")
uservice = UserService()
lg = get_logger(script_path=__file__)


@router.post("/send_mail")
async def send_email_to_user(emails: EmailModel):
    lg.info(f"Sending test email to: {emails}")
    subject = "Welcome to our app"
    send_email.delay(
        recipients=emails.emails,
        subject=subject,
        template_body={
            "email": emails.emails[0],
            "link": f"http://{settings.DOMAIN_NAME}",
        },
        template_name="verify_account.html",
    )
    return {"message": "Emails sent successfully"}


@router.post(
    path="/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=UserSignupResponse,
)
def create_user(user_data: UserCreateSchema, db: Session = Depends(dependency=get_db)):
    new_user = uservice.create_new_user(user_data=user_data, db=db)
    signup_token = create_url_safe_token(
        {"user_id": str(new_user.user_id), "email": new_user.email}
    )
    verification_link = f"http://{settings.DOMAIN_NAME}/api/{settings.VERSION or 'v1.1'}/user/verify_email?token={signup_token}"

    subject = "Verify your email for PromptCrafter"
    send_email.delay(
        recipients=[new_user.email],
        subject=subject,
        template_body={"email": new_user.email, "link": verification_link},
        template_name="verify_account.html",
    )
    lg.info(
        f"Verification email sent to: {new_user.email} with link: {verification_link}"
    )
    return {
        "message": "User created successfully, Please check your email for verification",
        "user": new_user,
    }


@router.get("/verify_email", status_code=status.HTTP_200_OK)
def verify_user_account(token: str, session: Session = Depends(get_db)):

    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email") if token_data else None
    if user_email:
        user = uservice.get_user_by_email(user_email, db=session)
        if not user:
            raise UserNotFound()

        uservice.update_user(user=user, user_data={"is_verified": True}, db=session)
        lg.info(f"User account verified: {user_email}")

        return JSONResponse(
            content={"message": "Account verified successfully."},
            status_code=status.HTTP_200_OK,
        )
    return JSONResponse(
        content={"message": "error occured during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@router.post(path="/id/{user_id}", response_model=UserOutSchema)
def get_user_by_id(user_id: str, db: Session = Depends(dependency=get_db)):
    user = uservice.get_user_by_id(user_id=user_id, db=db)
    return user


@router.post(path="/login", status_code=status.HTTP_200_OK)
async def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(dependency=get_db),
):
    # Check rate limiting
    attempts = await get_login_attempts(user_credentials.username)
    if attempts >= 5:
        raise HTTPException(
            status_code=429, detail="Too many login attempts. Try again later."
        )

    # first we need function in the service to verify the user credentials and return the user if valid
    user = uservice.get_user_by_email(email=user_credentials.username, db=db)

    if not user:
        await increment_login_attempts(user_credentials.username)
        raise InvalidCredentials()

    if not user.is_verified:
        await increment_login_attempts(user_credentials.username)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account not verified"
        )

    # verify the password
    if not verify_password(user_credentials.password, user.password):
        await increment_login_attempts(user_credentials.username)
        raise InvalidCredentials()

    # Reset attempts on successful login
    await reset_login_attempts(user_credentials.username)

    # second we need access token  generation function in the tools
    access_token = create_access_token(
        user_data={
            "user_id": user.user_id,
            "email": user.email,
            "is_admin": user.is_admin,
            "is_verified": user.is_verified,
        }
    )
    refresh_token = create_access_token(
        user_data={
            "user_id": user.user_id,
            "email": user.email,
            "is_admin": user.is_admin,
            "is_verified": user.is_verified,
        },
        refresh=True,
        expiry=timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRY_MINUTES),
    )

    # Store refresh token
    expires_at = datetime.now() + timedelta(
        minutes=settings.JWT_REFRESH_TOKEN_EXPIRY_MINUTES
    )
    uservice.store_refresh_token(user.user_id, refresh_token, expires_at, db)

    lg.info(f"User {user.email} logged in successfully")
    return JSONResponse(
        content={
            "message": "Login Successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {"email": user.email, "user_uid": str(user.user_uid)},
        }
    )


@router.get(path="/refresh", status_code=status.HTTP_200_OK)
def get_new_access_token(
    token: str = Depends(get_refresh_token), db: Session = Depends(get_db)
):
    lg.info("Refreshing access token")
    token_data = decode_access_token(token)
    if token_data is None or "user_id" not in token_data:
        raise InvalidToken()

    user_data = token_data
    user_id = user_data.get("user_id")
    email = user_data.get("email")

    user = uservice.get_user_by_email(email=email, db=db)
    if user is None or str(user.user_id) != user_id:
        raise InvalidToken()

    # Invalidate old refresh token
    uservice.invalidate_refresh_token(token, db)

    # Generate new access token
    new_access_token = create_access_token(
        user_data={
            "email": email,
            "user_id": user_id,
            "is_admin": user.is_admin,
            "is_verified": user.is_verified,
        }
    )

    # Generate new refresh token
    new_refresh_token = create_access_token(
        user_data={
            "user_id": user_id,
            "email": email,
            "is_admin": user.is_admin,
            "is_verified": user.is_verified,
        },
        refresh=True,
        expiry=timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRY_MINUTES),
    )

    # Store new refresh token
    expires_at = datetime.now() + timedelta(
        minutes=settings.JWT_REFRESH_TOKEN_EXPIRY_MINUTES
    )
    uservice.store_refresh_token(user_id, new_refresh_token, expires_at, db)

    lg.info(f"New tokens generated for user: {email}")
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/forgot-password")
def forgot_password(request: PasswordResetRequestSchema, db: Session = Depends(get_db)):
    user = uservice.get_user_by_email(request.email, db)
    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a reset link has been sent."}

    reset_token = create_url_safe_token(
        {"user_id": str(user.user_id), "email": user.email}
    )
    reset_link = f"http://{settings.DOMAIN_NAME}/api/{settings.VERSION or 'v1.1'}/user/reset-password?token={reset_token}"

    subject = "Password Reset for PromptCrafter"
    send_email.delay(
        recipients=[user.email],
        subject=subject,
        template_body={"email": user.email, "link": reset_link},
        template_name="verify_account.html",  # Reuse template
    )
    lg.info(f"Password reset email sent to: {user.email}")
    return {"message": "If the email exists, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(request: PasswordResetSchema, db: Session = Depends(get_db)):
    token_data = decode_url_safe_token(request.token)
    if not token_data:
        raise InvalidToken()

    user_id = token_data.get("user_id")
    email = token_data.get("email")
    user = uservice.get_user_by_email(email, db)
    if not user or str(user.user_id) != user_id:
        raise InvalidToken()

    # Validate new password
    uservice.validate_password_strength(request.new_password)

    # Update password
    hashed_password = hash_password(request.new_password)
    uservice.update_user(user=user, user_data={"password": hashed_password}, db=db)

    # Invalidate all tokens
    uservice.invalidate_all_user_refresh_tokens(user_id, db)

    lg.info(f"Password reset for user: {email}")
    return {"message": "Password reset successfully."}


@router.post(path="/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    token: str = Depends(get_access_token), db: Session = Depends(dependency=get_db)
):
    lg.info("Logging out user")
    token_data = decode_access_token(token)
    if token_data is None or "jti" not in token_data or "user_id" not in token_data:
        raise InvalidToken()

    jti = token_data["jti"]
    user_id = token_data["user_id"]
    add_jit_to_blocklist(jti)
    # Invalidate all refresh tokens for the user
    uservice.invalidate_all_user_refresh_tokens(user_id, db)
    lg.info(f"User {user_id} logged out, tokens invalidated")
    return JSONResponse(content={"message": "Logout successful"}, status_code=204)

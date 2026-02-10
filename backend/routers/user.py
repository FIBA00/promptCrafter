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
from core.custom_error_handlers import InvalidCredentials, InvalidToken
from core.schemas import (
    UserCreateSchema,
    UserOutSchema,
    UserSignupResponse,
)
from auth.oauth2 import (
    verify_password,
    create_access_token,
    decode_access_token,
)

from auth.dependencies import get_refresh_token, get_access_token
from utility.logger import get_logger
from services.user_service import UserService


router = APIRouter(prefix="/user", tags=["user"])
# router.mount("/static", StaticFiles(directory="static"), name="static")
uservice = UserService()
lg = get_logger(script_path=__file__)


# main routes


@router.post(
    path="/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=UserSignupResponse,
)
def create_user(user_data: UserCreateSchema, db: Session = Depends(dependency=get_db)):
    new_user = uservice.create_new_user(user_data=user_data, db=db)
    return {
        "message": "User created successfully, Please check your email for verification",
        "user": new_user,
    }


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

    # if not user.is_verified:
    #     await increment_login_attempts(user_credentials.username)
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN, detail="User account not verified"
    #     )

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
            "user": {"email": user.email, "user_id": str(user.user_id)},
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


@router.post(path="/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    token: str = Depends(get_access_token), db: Session = Depends(dependency=get_db)
):
    lg.info("Logging out user")
    token_data = decode_access_token(token)
    if token_data is None or "jti" not in token_data or "user_id" not in token_data:
        raise InvalidToken()

    jti = token_data["jti"]
    user_id = token_data["user_id"]
    await add_jit_to_blocklist(jti)
    # Invalidate all refresh tokens for the user
    uservice.invalidate_all_user_refresh_tokens(user_id, db)
    lg.info(f"User {user_id} logged out, tokens invalidated")
    return JSONResponse(content={"message": "Logout successful"}, status_code=204)

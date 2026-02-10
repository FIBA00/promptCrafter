# user page
from datetime import timedelta, datetime
from fastapi import APIRouter, status, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

from sqlalchemy.orm import Session

# our custom module imports
from db.database import get_db
from db.redis import add_jit_to_blocklist
from core.config import settings
from core.custom_error_handlers import InvalidToken
from core.schemas import UserOutSchema
from auth.oauth2 import create_access_token, decode_access_token

from auth.dependencies import get_refresh_token, get_access_token
from utility.logger import get_logger
from services.user_service import UserService


router = APIRouter(prefix="/user", tags=["user"])
# router.mount("/static", StaticFiles(directory="static"), name="static")
uservice = UserService()
lg = get_logger(script_path=__file__)


# main routes


@router.post(path="/id/{user_id}", response_model=UserOutSchema)
def get_user_by_id(user_id: str, db: Session = Depends(dependency=get_db)):
    user = uservice.get_user_by_id(user_id=user_id, db=db)
    return user


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


@router.get("/login/google")
def login_google():
    authorization_url = uservice.get_google_login_url()
    return RedirectResponse(authorization_url)


@router.get("/auth/google")
def auth_google(request: Request, db: Session = Depends(get_db)):
    result = uservice.process_google_auth(str(request.url), db)
    return JSONResponse(content=result)

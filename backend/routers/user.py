# user page
from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from db.database import get_db
from core.schemas import (
    UserCreateSchema,
    UserOutSchema,
    TokenOutSchema,
    UserLoginSchema,
)
from core.custom_error_handlers import InvalidCredentials
from core.oauth2 import verify_password, create_access_token

from utility.logger import get_logger
from services.user_service import UserService

router = APIRouter(prefix="/user", tags=["user"])
# router.mount("/static", StaticFiles(directory="static"), name="static")
uservice = UserService()
lg = get_logger(script_path=__file__)


@router.post(
    path="/", status_code=status.HTTP_201_CREATED, response_model=UserOutSchema
)
def create_user(user_data: UserCreateSchema, db: Session = Depends(dependency=get_db)):
    new_user = uservice.create_new_user(user_data=user_data, db=db)
    return new_user


@router.post(path="/id/{user_id}", response_model=UserOutSchema)
def get_user_by_id(user_id: str, db: Session = Depends(dependency=get_db)):
    user = uservice.get_user_by_id(user_id=user_id, db=db)
    return user


@router.post(path="/login", response_model=TokenOutSchema)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(dependency=get_db),
):
    # first we need function in the service to verify the user credentials and return the user if valid
    user = uservice.get_user_by_email(email=user_credentials.username, db=db)
    if not user:
        raise InvalidCredentials()

    # verify the password
    if not verify_password(user_credentials.password, user.password):
        raise InvalidCredentials()

    # second we need access token  generation function in the tools
    access_token = create_access_token(
        user_data={
            "user_id": user.user_id,
            "email": user.email,
            "is_admin": user.is_admin,
            "is_verified": user.is_verified,
        }
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post(path="/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(user_id: str, db: Session = Depends(dependency=get_db)):
    # implement token blacklisting on the server side for added security
    pass

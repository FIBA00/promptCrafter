# user page
from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from pydantic import EmailStr

from schema.schemas import UserCreateSchema, UserOutSchema
from utility.logger import get_logger
from db.database import get_db
from services.user_service import UserService


router = APIRouter(prefix="/user", tags=["auth"])
# router.mount("/static", StaticFiles(directory="static"), name="static")
uservice = UserService()
lg = get_logger(script_path=__file__)


@router.post(
    path="/", status_code=status.HTTP_201_CREATED, response_model=UserOutSchema
)
def create_user(user_data: UserCreateSchema, db: Session = Depends(dependency=get_db)):
    new_user = uservice.create_new_user(user_data=user_data, db=db)
    return new_user


@router.post(path="/id/{user_id}")
def get_user_by_id(user_id: str, db: Session = Depends(dependency=get_db)):
    user = uservice.get_user_by_id(user_id=user_id, db=db)
    return user


@router.post("/email/{user_email}")
def get_user_by_email(user_email: EmailStr, db: Session = Depends(dependency=get_db)):
    user = uservice.get_user_by_email(email=user_email, db=db)
    return user


@router.get(path="/{id}")
def login(id: int, db: Session = Depends(dependency=get_db)):
    pass

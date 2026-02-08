# user page
import uuid
from typing import List
from fastapi import APIRouter, status, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import EmailStr

from core.models import User
from schema.schemas import UserCreateSchema, UserOutSchema
from utility.logger import get_logger
from utility.tools import hash_password
from db.database import get_db
from services.user_service import UserService


router = APIRouter(prefix="/user", tags=["auth"])
# router.mount("/static", StaticFiles(directory="static"), name="static")
uservice = UserService()
lg = get_logger(__file__)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserOutSchema)
def create_user(user_data: UserCreateSchema, db: Session = Depends(get_db)):
    new_user = uservice.create_new_user(user_data=user_data, db=db)
    return new_user


@router.post("/id/{user_id}")
def get_user_by_id(user_id: str, db: Session = Depends(get_db)):
    user = uservice.get_user_by_id(user_id=user_id, db=db)
    return user


@router.post("/email/{user_email}")
def get_user_by_email(user_email: EmailStr, db: Session = Depends(get_db)):
    user = uservice.get_user_by_email(email=user_email, db=db)
    return user


@router.get("/{id}")
def login(id: int, db: Session = Depends(get_db)):
    pass

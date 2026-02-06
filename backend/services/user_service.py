import uuid
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import EmailStr


from schema.schemas import UserCreateSchema, UserOutSchema
from core.models import User
from utility.logger import get_logger
from utility.tools import hash_password

lg = get_logger(__file__)


class UserService:
    def create_new_user(self, user_data: UserCreateSchema, db: Session):
        try:
            # create new user, first conver the shcema to dictionary
            user_data_dict = user_data.model_dump()
            # check if the user has an id with the request
            if not user_data_dict.get("user_id"):
                user_data_dict["user_id"] = str(uuid.uuid4())

            # create a data base model
            new_user = User(**user_data_dict)
            # hash the password
            new_user.password = hash_password(user_data_dict["password"])

            lg.debug(f"Creating new user: {new_user.user_id}")

            # append the user to database
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            return UserOutSchema.model_validate(new_user)
        except SQLAlchemyError as e:
            # This catches ANY database error (connection lost, constraint violation, etc.)
            db.rollback()  # CRITICAL: Reset the db so it's clean for the next request
            lg.error(f"Database Error saving prompt: {str(e)}")
            raise e  # Re-raise it so the router knows something went wrong

        except Exception as e:
            # This catches any other unexpected Python error (like a bug in our code)
            lg.error(f"Unexpected Error in save_prompt: {str(e)}")
            raise e

    def get_all_user(self, db: Session):
        lg.debug("Getting all the prompts.")
        return None

    def get_user_by_id(self, user_id: str, db: Session):
        try:
            lg.debug(f"Getting user by id: {user_id}")
            user = db.query(User).filter(User.user_id == user_id).first()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"user with id: {user_id}, was not found",
                )
            lg.debug(f"Found user by id: {user_id}: , user email: {user.email}")
            return UserOutSchema.model_validate(user)
        except SQLAlchemyError as e:
            # This catches ANY database error (connection lost, constraint violation, etc.)
            db.rollback()  # CRITICAL: Reset the db so it's clean for the next request
            lg.error(f"Database Error saving prompt: {str(e)}")
            raise e  # Re-raise it so the router knows something went wrong

        except Exception as e:
            # This catches any other unexpected Python error (like a bug in our code)
            lg.error(f"Unexpected Error in save_prompt: {str(e)}")
            raise e

    def get_user_by_email(self, email: EmailStr, db: Session):
        try:
            lg.debug(f"Getting user by email: {email}")
            user = db.query(User).filter(User.email == email).first()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"user with email: {email}, was not found",
                )
            lg.debug(f"Found user by email: {email}: , user id: {user.user_id}")
            return UserOutSchema.model_validate(user)
        except SQLAlchemyError as e:
            # This catches ANY database error (connection lost, constraint violation, etc.)
            db.rollback()  # CRITICAL: Reset the db so it's clean for the next request
            lg.error(f"Database Error saving prompt: {str(e)}")
            raise e  # Re-raise it so the router knows something went wrong

        except Exception as e:
            # This catches any other unexpected Python error (like a bug in our code)
            lg.error(f"Unexpected Error in save_prompt: {str(e)}")
            raise e

    def delete_user(self, email: str, db: Session):
        return None

    def update_user(self, email: str, db: Session):
        return None

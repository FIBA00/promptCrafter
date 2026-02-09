import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import EmailStr


from core.schemas import UserCreateSchema, UserOutSchema
from db.models import User
from utility.logger import get_logger
from core.oauth2 import hash_password
from core.custom_error_handlers import (
    UserAlreadyExists,
    UserNotFound,
    InvalidCredentials,
    RateLimitExceeded,
)

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
        except IntegrityError as e:
            # Likely duplicate email
            db.rollback()
            lg.error(f"Integrity error creating user: {str(e)}")
            raise UserAlreadyExists()
        except SQLAlchemyError as e:
            # This catches ANY database error (connection lost, constraint violation, etc.)
            db.rollback()  # CRITICAL: Reset the db so it's clean for the next request
            lg.error(f"Database Error saving user: {str(e)}")
            raise e  # Re-raise it so the router knows something went wrong

        except Exception as e:
            # This catches any other unexpected Python error (like a bug in our code)
            lg.error(f"Unexpected Error in save_user: {str(e)}")
            raise e

    def get_user_by_id(self, user_id: str, db: Session):
        try:
            lg.debug(f"Getting user by id: {user_id}")
            user = db.query(User).filter(User.user_id == user_id).first()
            if user is None:
                raise UserNotFound()
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
                raise UserNotFound()
            lg.debug(f"Found user by email: {email}: , user id: {user.user_id}")
            return user  # NOTE:do not validate the user here becuase we need all the fields for the login function including hashed password!
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

    def check_daily_limit(self, db: Session, user_id: str, cost: int = 1) -> bool:
        """
        Check if user has enough tokens for the request.
        Resets quota if it's a new day.
        Raises RateLimitExceeded if not enough tokens.
        """
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise UserNotFound

            # Check date
            today = datetime.utcnow().date()
            if user.last_token_reset != today:
                # Reset
                lg.debug(f"Resetting tokens for user {user_id}")
                user.tokens_used_today = 0
                user.last_token_reset = today
                db.add(user)
                db.commit()
                db.refresh(user)

            if user.tokens_used_today + cost > user.daily_token_limit:
                lg.warning(f"User {user_id} exceeded daily token limit")
                raise RateLimitExceeded

            # Deduct (add usage)
            user.tokens_used_today += cost
            db.add(user)
            db.commit()
            db.refresh(user)

            lg.debug(
                f"User {user_id} used {cost} tokens. Balance: {user.daily_token_limit - user.tokens_used_today}"
            )
            return True

        except RateLimitExceeded as e:
            raise e
        except Exception as e:
            lg.error(f"Error checking daily limit: {str(e)}")
            raise e

    def update_user(self, email: str, db: Session):
        return None

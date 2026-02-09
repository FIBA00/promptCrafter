import uuid
import bcrypt
from jose import jwt, JWTError

from datetime import datetime, timedelta
from .logger import get_logger
from core.config import settings

lg = get_logger(__file__)


def hash_password(password: str) -> str:
    try:
        lg.debug(f"Hashing passowrd: {password}")
        truncated_password = password.encode("utf-8")[:72]
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(truncated_password, salt).decode("utf-8")
        lg.debug(f"Hashed password: {hashed_password}")
        if hashed_password is not None:
            return hashed_password

        return None
    except Exception as e:
        lg.error(f"Error hashing password: {str(e)}")
        raise e


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        lg.debug(
            f"Verifing password: {plain_password} with hashed password: {hashed_password}"
        )
        truncated_password = plain_password.encode("utf-8")[:72]
        verified_password = bcrypt.checkpw(
            truncated_password, hashed_password.encode("utf-8")
        )
        if not verified_password:
            lg.debug("Failed to verify password")
            return False

        lg.debug("Password verified successfully")
        return True
    except Exception as e:
        lg.error(f"Error verifying password: {str(e)}")
        raise e


def create_access_token(
    user_data: dict, expiry: timedelta = None, refresh: bool = False
) -> str:
    """
    Create a JWT access token for the given user data. If refresh is True, create a refresh token instead.
    Args:
        user_data (dict): A dictionary containing user information to include in the token payload.
        expiry (timedelta, optional): The expiration time for the token. Defaults to None, which means no expiration.
        refresh (bool, optional): Whether to create a refresh token instead of an access token. Defaults to False.
    Returns:
        str: The generated JWT token as a string.
    """
    try:
        payload = {}
        # construct the payload with user data, we can include user_id, email,
        # and any other relevant information

        payload["user_id"] = user_data.get("user_id", user_data.get("user_id"))
        payload["email"] = user_data.get("email", user_data.get("email"))
        payload["exp"] = datetime.now() + (
            expiry
            if expiry
            else timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        payload["jti"] = str(uuid.uuid4())  # unique identifier for the token
        payload["refresh"] = refresh  # flag to indicate if this is a refresh token

        token = jwt.encode(
            claims=payload,
            key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        return token
    except Exception as e:
        lg.error(f"Error creating access token: {str(e)}")
        raise e


def decode_access_token(token: str) -> dict:
    """
    Decode a JWT access token and return the payload as a dictionary.
    Args:
        token (str): The JWT token to decode.
    Returns:
        dict: The decoded token payload as a dictionary.
    Raises:
        JWTError: If the token is invalid or cannot be decoded.
    """
    try:
        token_data = jwt.decode(
            token=token,
            key=settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return token_data
    except JWTError as e:
        lg.error(f"Error decoding access token: {str(e)}")
        raise e
    except Exception as e:
        lg.error(f"Unexpected error decoding access token: {str(e)}")
        raise e

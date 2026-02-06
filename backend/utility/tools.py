import bcrypt
from .logger import get_logger

lg = get_logger(__file__)


def hash_password(password: str) -> str:
    lg.debug(f"Hashing passowrd: {password}")
    truncated_password = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(truncated_password, salt).decode("utf-8")
    lg.debug(f"Hashed password: {hashed_password}")
    if hashed_password is not None:
        return hashed_password

    return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
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

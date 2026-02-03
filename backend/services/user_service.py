from sqlalchemy.orm import Session

from utility.logger import get_logger

lg = get_logger(__file__)


class UserService:
    def get_all_user(self, session: Session):
        lg.debug("Getting all the prompts.")
        return None

    def get_user_by_id(self, id: str, session: Session):
        lg.debug(f"Getting user by id: {id}")
        user = None
        return user

    def get_user_by_email(self, email: str, session: Session):
        user = None
        return user

    def delete_user(self, email: str, session: Session):
        return None

    def update_user(self, email: str, session: Session):
        return None

import sys
import os

# Add the directory containing this file to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal
from db.models import User
from utility.logger import get_logger

lg = get_logger(__file__)


def make_user_admin(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            lg.error(f"User with email {email} not found.")
            print(f"User with email {email} not found.")
            return

        user.is_admin = True
        user.is_verified = True
        db.commit()
        lg.info(f"User {email} has been promoted to admin and verified.")
        print(f"SUCCESS: User {email} is now an admin.")
    except Exception as e:
        lg.error(f"Error promoting user: {e}")
        print(f"ERROR: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_superuser.py <email>")
        sys.exit(1)

    email = sys.argv[1]
    make_user_admin(email)

from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from db.models import User, Prompts, StructuredPrompts
from core.oauth2 import verify_password, create_access_token, decode_access_token
from db.database import SessionLocal
from utility.logger import get_logger

lg = get_logger(__file__)


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return False

            if not verify_password(password, user.password):
                return False

            if not user.is_admin:
                # Optional: Log attempt by non-admin
                return False

            # Create token
            access_token = create_access_token(
                user_data={
                    "user_id": user.user_id,
                    "email": user.email,
                    "is_admin": user.is_admin,
                    "is_verified": user.is_verified,
                }
            )
            request.session.update({"token": access_token})
            return True
        except Exception as e:
            lg.error(f"Admin login error: {e}")
            return False
        finally:
            db.close()

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        try:
            payload = decode_access_token(token)
            if not payload.get("is_admin"):
                return False
            return True
        except Exception:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)


class UserAdmin(ModelView, model=User):
    column_list = [
        User.user_id,
        User.username,
        User.email,
        User.is_admin,
        User.is_verified,
        User.created_at,
    ]
    icon = "fa-solid fa-user"
    name = "User"
    name_plural = "Users"
    column_searchable_list = [User.username, User.email]
    column_sortable_list = [User.created_at, User.is_admin]


class PromptAdmin(ModelView, model=Prompts):
    column_list = [Prompts.title, Prompts.role, Prompts.author, Prompts.created_at]
    icon = "fa-solid fa-comment"
    name = "Prompt"
    name_plural = "Prompts"
    column_searchable_list = [Prompts.title, Prompts.role]


class StructuredPromptAdmin(ModelView, model=StructuredPrompts):
    column_list = [
        StructuredPrompts.prompt_id,
        StructuredPrompts.original_prompt,
        StructuredPrompts.created_at,
    ]
    icon = "fa-solid fa-robot"
    name = "Structured Prompt"
    name_plural = "Structured Prompts"

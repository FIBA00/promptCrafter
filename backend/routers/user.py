# user page
from fastapi import (
    APIRouter,
    status,
    Depends,
    BackgroundTasks,
    HTTPException,
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from db.database import get_db
from db.redis import add_jit_to_blocklist
from core.schemas import (
    UserCreateSchema,
    UserOutSchema,
    TokenOutSchema,
    UserLoginSchema,
    EmailModel,
)
from core.config import settings
from core.send_mail import mail, create_message
from core.celery_tasks import send_email
from core.custom_error_handlers import InvalidCredentials
from core.oauth2 import (
    verify_password,
    create_access_token,
    create_url_safe_token,
    decode_url_safe_token,
)
from core.custom_error_handlers import (
    UserAlreadyExists,
    UserNotFound,
    InvalidCredentials,
    RateLimitExceeded,
)


from utility.logger import get_logger
from services.user_service import UserService


router = APIRouter(prefix="/user", tags=["user"])
# router.mount("/static", StaticFiles(directory="static"), name="static")
uservice = UserService()
lg = get_logger(script_path=__file__)


@router.post("/send_mail")
async def send_email_to_user(emails: EmailModel):
    lg.info(f"Sending test email to: {emails}")
    subject = "Welcome to our app"
    send_email.delay(
        recipients=emails.emails,
        subject=subject,
        template_body={
            "email": emails.emails[0],
            "link": f"http://{settings.DOMAIN_NAME}",
        },
        template_name="verify_account.html",
    )
    return {"message": "Emails sent successfully"}


@router.post(
    path="/signup", status_code=status.HTTP_201_CREATED, response_model=UserOutSchema
)
def create_user(user_data: UserCreateSchema, db: Session = Depends(dependency=get_db)):
    new_user = uservice.create_new_user(user_data=user_data, db=db)
    signup_token = create_url_safe_token(
        {"user_id": new_user.user_id, "email": new_user.email}
    )
    verification_link = f"http://{settings.DOMAIN_NAME}/api/{settings.VERSION or 'v1.1'}/user/verify_email?token={signup_token}"

    subject = "Verify your email for PromptCrafter"
    send_email.delay(
        recipients=[new_user.email],
        subject=subject,
        template_body={"email": new_user.email, "link": verification_link},
        template_name="verify_account.html",
    )
    lg.info(
        f"Verification email sent to: {new_user.email} with link: {verification_link}"
    )
    return {
        "message": "User created successfully, Please check your email for verification",
        "user": new_user,
    }


@router.get("/verify_email", status_code=status.HTTP_200_OK)
def verify_user_account(token: str, session: Session = Depends(get_db)):

    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email") if token_data else None
    if user_email:
        user = uservice.get_user_by_email(user_email, db=session)
        if not user:
            raise UserNotFound()

        uservice.update_user(user=user, user_data={"is_verified": True}, db=session)
        lg.info(f"User account verified: {user_email}")

        return JSONResponse(
            content={"message": "Account verified successfully."},
            status_code=status.HTTP_200_OK,
        )
    return JSONResponse(
        content={"message": "error occured during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


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

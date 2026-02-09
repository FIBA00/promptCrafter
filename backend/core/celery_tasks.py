from celery import Celery
from asgiref.sync import async_to_sync

from .send_mail import mail, create_message
from utility.logger import get_logger

lg = get_logger(__file__)
c_app = Celery()
c_app.config_from_object("core.config")


@c_app.task()
def send_email(
    recipients: list[str], subject: str, template_body: dict, template_name: str
):
    message = create_message(
        recipients=recipients, subject=subject, template_body=template_body
    )
    async_to_sync(mail.send_message)(message, template_name=template_name)
    lg.info(f"Email sent to : {recipients}")

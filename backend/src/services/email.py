from pathlib import Path
from typing import List, Dict, Any
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
import datetime

from ..config import settings
from ..utils.logging import get_logger

logger = get_logger(__name__)

# Determine template directory
TEMPLATE_FOLDER = Path(__file__).parent.parent / 'templates' / 'email'

# Configure FastMail
conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASS,
    MAIL_FROM=settings.FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_FROM_NAME=settings.FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=TEMPLATE_FOLDER
)

class EmailService:
    @staticmethod
    async def send_email(
        recipients: List[EmailStr],
        subject: str,
        template_name: str,
        template_body: Dict[str, Any]
    ):
        """
        Send an email using a template.
        """
        # For dev/debug, always log the link
        if "link" in template_body:
            logger.info(f"=== DEBUG EMAIL LINK ===\n{template_body['link']}\n========================")

        # 1. Try Resend if configured
        if settings.RESEND_API_KEY:
            try:
                import resend
                resend.api_key = settings.RESEND_API_KEY
                
                # Render template manually using Jinja2
                from jinja2 import Environment, FileSystemLoader
                env = Environment(loader=FileSystemLoader(str(TEMPLATE_FOLDER)))
                template = env.get_template(template_name)
                html_content = template.render(**template_body)
                
                params = {
                    "from": f"{settings.FROM_NAME} <{settings.FROM_EMAIL}>",
                    "to": recipients,
                    "subject": subject,
                    "html": html_content
                }
                
                r = resend.Emails.send(params)
                logger.info(f"Email sent via Resend to {recipients}: {r}")
                return
            except Exception as e:
                logger.error(f"Resend failed: {e}. Falling back to SMTP if available.")
        
        # 2. Fallback to SMTP
        if not settings.SMTP_HOST or not settings.SMTP_USER:
             if not settings.RESEND_API_KEY:
                logger.warning("Neither Resend nor SMTP configured.")
             return

        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            template_body=template_body,
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        
        try:
            await fm.send_message(message, template_name=template_name)
            logger.info(f"Email sent via SMTP to {recipients}")
        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {e}")
            raise

import logging
from typing import Any

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


async def send_order_confirmation(
    order_number: str,
    email: str,
    username: str,
    total_amount: str,
    items_count: int,
) -> bool:
    message = {
        "to": email,
        "subject": f"Order Confirmation - {order_number}",
        "body": f"""
Hello {username},

Your order #{order_number} has been confirmed!

Order Details:
- Total Amount: {total_amount}
- Items: {items_count}

Thank you for shopping with us!

Best regards,
Online Shop Team
""",
    }
    return await _send_email(message)


async def send_order_paid_notification(
    order_number: str,
    email: str,
    username: str,
    total_amount: str,
) -> bool:
    message = {
        "to": email,
        "subject": f"Payment Confirmed - {order_number}",
        "body": f"""
Hello {username},

Great news! Your payment for order #{order_number} has been confirmed.

Amount Paid: {total_amount}

We will notify you when your order ships.

Best regards,
Online Shop Team
""",
    }
    return await _send_email(message)


async def send_order_cancelled_notification(
    order_number: str,
    email: str,
    username: str,
    reason: str | None = None,
) -> bool:
    reason_text = f"\nReason: {reason}" if reason else ""
    message = {
        "to": email,
        "subject": f"Order Cancelled - {order_number}",
        "body": f"""
Hello {username},

Your order #{order_number} has been cancelled.{reason_text}

If you have any questions, please contact our support.

Best regards,
Online Shop Team
""",
    }
    return await _send_email(message)


async def send_welcome_email(
    email: str,
    username: str,
) -> bool:
    message = {
        "to": email,
        "subject": "Welcome to Online Shop!",
        "body": f"""
Hello {username},

Welcome to Online Shop!

We're excited to have you as a member of our community.
Start exploring our products and enjoy your shopping experience.

Best regards,
Online Shop Team
""",
    }
    return await _send_email(message)


async def send_password_reset_email(
    email: str,
    username: str,
    reset_token: str,
) -> bool:
    message = {
        "to": email,
        "subject": "Password Reset Request",
        "body": f"""
Hello {username},

You requested a password reset. Use the following token:

{reset_token}

If you didn't request this, please ignore this email.

Best regards,
Online Shop Team
""",
    }
    return await _send_email(message)


async def _send_email(message: dict[str, Any]) -> bool:
    if settings.EMAIL_MODE == "console":
        logger.info("=== EMAIL NOTIFICATION ===")
        logger.info(f"To: {message['to']}")
        logger.info(f"Subject: {message['subject']}")
        logger.info(f"Body:\n{message['body']}")
        logger.info("=== END EMAIL ===")
        return True

    if settings.EMAIL_MODE == "resend":
        return await _send_via_resend(message)

    logger.warning(f"Unknown EMAIL_MODE: {settings.EMAIL_MODE}")
    return False


async def _send_via_resend(message: dict[str, Any]) -> bool:
    try:
        import resend
    except ImportError:
        logger.error("resend package not installed")
        return False

    if not settings.RESEND_API_KEY:
        logger.error("RESEND_API_KEY not configured")
        return False

    resend.api_key = settings.RESEND_API_KEY
    try:
        result = resend.Emails.send(
            {
                "from": settings.EMAIL_FROM,
                "to": message["to"],
                "subject": message["subject"],
                "text": message["body"],
            }
        )
        logger.info(f"Email sent via Resend: {result}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email via Resend: {e}")
        return False

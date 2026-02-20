"""Email service for sending verification and notification emails."""

import base64
import logging
from typing import Optional, List, Tuple

import httpx
from jinja2 import Environment, FileSystemLoader

from backend.config import config
from backend.exceptions import EmailError

logger = logging.getLogger(__name__)

# Setup Jinja2 for email templates
email_templates = Environment(
    loader=FileSystemLoader("frontend/templates/emails"),
    autoescape=True,
)


class EmailService:
    """
    Email service using SendGrid API.

    Handles sending verification emails and other transactional emails.
    """

    SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"

    def __init__(
        self,
        api_key: Optional[str] = None,
        from_address: Optional[str] = None,
        from_name: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize email service.

        Args:
            api_key: SendGrid API key (defaults to config)
            from_address: Sender email address (defaults to config)
            from_name: Sender display name (defaults to config)
            base_url: Base URL for verification links (defaults to config)
        """
        self.api_key = api_key or config.email_api_key
        self.from_address = from_address or config.email_from_address
        self.from_name = from_name or config.email_from_name
        self.base_url = base_url or config.base_url

    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return bool(self.api_key and self.from_address)

    async def send_verification_email(
        self, to_email: str, token: str, name: Optional[str] = None
    ) -> bool:
        """
        Send email verification link to user.

        Args:
            to_email: Recipient email address
            token: Verification token
            name: Optional recipient name for personalization

        Returns:
            True if email sent successfully

        Raises:
            EmailError: If email sending fails
        """
        if not self.is_configured():
            logger.warning("Email service not configured, skipping verification email")
            return False

        verification_url = f"{self.base_url}/api/auth/verify-email/{token}"
        subject = "Verify your email - Your Newsletter, Your Way"

        # Build personalized greeting
        greeting = f"Hi {name}," if name else "Hi there,"

        html_content = self._build_verification_email_html(greeting, verification_url)
        text_content = self._build_verification_email_text(greeting, verification_url)

        return await self._send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )

    async def send_welcome_email(self, to_email: str, name: Optional[str] = None) -> bool:
        """
        Send welcome email after verification.

        Args:
            to_email: Recipient email address
            name: Optional recipient name

        Returns:
            True if email sent successfully
        """
        if not self.is_configured():
            logger.warning("Email service not configured, skipping welcome email")
            return False

        greeting = f"Hi {name}," if name else "Hi there,"
        subject = "Welcome to Your Newsletter, Your Way!"

        html_content = self._build_welcome_email_html(greeting)
        text_content = self._build_welcome_email_text(greeting)

        return await self._send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )

    async def send_feedback_email(
        self,
        feedback_text: str,
        user_name: Optional[str] = None,
        user_email: Optional[str] = None,
        attachments: Optional[List[Tuple[str, bytes, str]]] = None,
    ) -> bool:
        """
        Send user feedback to the feedback email address.

        Args:
            feedback_text: The feedback message from the user
            user_name: Optional name of the user submitting feedback
            user_email: Optional email of the user submitting feedback
            attachments: Optional list of (filename, content, content_type) tuples

        Returns:
            True if email sent successfully

        Raises:
            EmailError: If email sending fails
        """
        if not self.is_configured():
            logger.warning("Email service not configured, skipping feedback email")
            return False

        # Feedback recipient email
        feedback_recipient = "yournewsletter.yourway@gmail.com"
        subject = "User Feedback - Your Newsletter, Your Way"

        html_content = self._build_feedback_email_html(
            feedback_text, user_name=user_name, user_email=user_email
        )
        text_content = self._build_feedback_email_text(
            feedback_text, user_name=user_name, user_email=user_email
        )

        return await self._send_email_with_attachments(
            to_email=feedback_recipient,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            attachments=attachments,
        )

    async def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
    ) -> bool:
        """
        Send email via SendGrid API.

        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML body
            text_content: Plain text body

        Returns:
            True if sent successfully

        Raises:
            EmailError: If sending fails
        """
        payload = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": self.from_address, "name": self.from_name},
            "subject": subject,
            "content": [
                {"type": "text/plain", "value": text_content},
                {"type": "text/html", "value": html_content},
            ],
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.SENDGRID_API_URL,
                    json=payload,
                    headers=headers,
                    timeout=30.0,
                )

                if response.status_code in (200, 202):
                    logger.info(f"Email sent successfully to {to_email}")
                    return True
                else:
                    logger.error(f"SendGrid API error: {response.status_code} - {response.text}")
                    raise EmailError(
                        "send",
                        f"SendGrid returned status {response.status_code}",
                    )

        except httpx.RequestError as e:
            logger.error(f"Email request failed: {e}")
            raise EmailError("send", f"Request failed: {str(e)}")

    async def _send_email_with_attachments(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
        attachments: Optional[List[Tuple[str, bytes, str]]] = None,
    ) -> bool:
        """
        Send email with optional attachments via SendGrid API.

        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML body
            text_content: Plain text body
            attachments: Optional list of (filename, content, content_type) tuples

        Returns:
            True if sent successfully

        Raises:
            EmailError: If sending fails
        """
        payload = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": self.from_address, "name": self.from_name},
            "subject": subject,
            "content": [
                {"type": "text/plain", "value": text_content},
                {"type": "text/html", "value": html_content},
            ],
        }

        # Add attachments if provided
        if attachments:
            attachment_list: list[dict[str, str]] = []
            for filename, content, content_type in attachments:
                # SendGrid requires base64-encoded content
                encoded_content = base64.b64encode(content).decode("utf-8")
                attachment_list.append(
                    {
                        "content": encoded_content,
                        "filename": filename,
                        "type": content_type,
                        "disposition": "attachment",
                    }
                )
            payload["attachments"] = attachment_list

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.SENDGRID_API_URL,
                    json=payload,
                    headers=headers,
                    timeout=60.0,  # Longer timeout for attachments
                )

                if response.status_code in (200, 202):
                    logger.info(f"Email with attachments sent successfully to {to_email}")
                    return True
                else:
                    logger.error(f"SendGrid API error: {response.status_code} - {response.text}")
                    raise EmailError(
                        "send",
                        f"SendGrid returned status {response.status_code}",
                    )

        except httpx.RequestError as e:
            logger.error(f"Email request failed: {e}")
            raise EmailError("send", f"Request failed: {str(e)}")

    def _build_verification_email_html(self, greeting: str, verification_url: str) -> str:
        """Build HTML content for verification email."""
        template = email_templates.get_template("verification_email.html")
        return template.render(greeting=greeting, verification_url=verification_url)

    def _build_verification_email_text(self, greeting: str, verification_url: str) -> str:
        """Build plain text content for verification email."""
        template = email_templates.get_template("verification_email.txt")
        return template.render(greeting=greeting, verification_url=verification_url)

    def _build_welcome_email_html(self, greeting: str) -> str:
        """Build HTML content for welcome email."""
        template = email_templates.get_template("welcome_email.html")
        return template.render(greeting=greeting, base_url=self.base_url)

    def _build_welcome_email_text(self, greeting: str) -> str:
        """Build plain text content for welcome email."""
        template = email_templates.get_template("welcome_email.txt")
        return template.render(greeting=greeting, base_url=self.base_url)

    def _build_feedback_email_html(
        self,
        feedback_text: str,
        user_name: Optional[str] = None,
        user_email: Optional[str] = None,
    ) -> str:
        """Build HTML content for feedback email."""
        template = email_templates.get_template("feedback_email.html")
        return template.render(
            feedback_text=feedback_text,
            user_name=user_name,
            user_email=user_email,
        )

    def _build_feedback_email_text(
        self,
        feedback_text: str,
        user_name: Optional[str] = None,
        user_email: Optional[str] = None,
    ) -> str:
        """Build plain text content for feedback email."""
        template = email_templates.get_template("feedback_email.txt")
        return template.render(
            feedback_text=feedback_text,
            user_name=user_name,
            user_email=user_email,
        )

    async def send_analytics_report(
        self,
        to_email: str,
        analysis: dict,
    ) -> bool:
        """
        Send feed analytics report email.

        Args:
            to_email: Recipient email address
            analysis: Analysis results from AIAnalyticsService

        Returns:
            True if email sent successfully

        Raises:
            EmailError: If email sending fails
        """
        if not self.is_configured():
            logger.warning("Email service not configured, skipping analytics report")
            return False

        date = analysis.get("date", "Unknown")
        subject = f"Feed Analytics Report - {date}"

        # Extract data for template
        data = analysis.get("data", {})
        copy_url = f"{self.base_url}/api/analytics/report"
        template_vars = {
            "date": date,
            "total_articles": data.get("total_articles", 0),
            "total_selected": data.get("total_selected", 0),
            "acceptance_rate": data.get("acceptance_rate", 0),
            "summary": analysis.get("summary", "No summary available"),
            "highlights": analysis.get("highlights", []),
            "action_items": analysis.get("action_items", []),
            "copy_url": copy_url,
        }

        html_content = self._build_analytics_report_html(**template_vars)
        text_content = self._build_analytics_report_text(**template_vars)

        return await self._send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )

    def _build_analytics_report_html(self, **kwargs) -> str:
        """Build HTML content for analytics report email."""
        template = email_templates.get_template("analytics_report.html")
        return template.render(**kwargs)

    def _build_analytics_report_text(self, **kwargs) -> str:
        """Build plain text content for analytics report email."""
        template = email_templates.get_template("analytics_report.txt")
        return template.render(**kwargs)


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get global email service singleton."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

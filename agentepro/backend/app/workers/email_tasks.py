from __future__ import annotations

import asyncio

from app.services.notification_service import send_email, send_welcome_email
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.email_tasks.send_transactional_email")
def send_transactional_email(to: str, subject: str, html: str) -> bool:
    """Envía un email transaccional desde un worker Celery."""
    return asyncio.run(send_email(to, subject, html))


@celery_app.task(name="app.workers.email_tasks.send_welcome")
def send_welcome(
    to: str,
    business_name: str,
    dashboard_url: str,
    webhook_url: str,
    phone_number: str | None = None,
    temp_password: str | None = None,
) -> bool:
    return asyncio.run(
        send_welcome_email(
            to,
            business_name=business_name,
            dashboard_url=dashboard_url,
            webhook_url=webhook_url,
            phone_number=phone_number,
            temp_password=temp_password,
        )
    )

from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "agentepro",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.workers.email_tasks",
        "app.workers.reminder_tasks",
        "app.workers.maintenance_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Lima",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    worker_max_tasks_per_child=200,
)

# Tareas periódicas (beat)
celery_app.conf.beat_schedule = {
    "send-appointment-reminders": {
        "task": "app.workers.reminder_tasks.send_appointment_reminders",
        "schedule": 3600.0,  # cada hora
    },
    "reset-monthly-usage": {
        "task": "app.workers.maintenance_tasks.reset_monthly_usage",
        "schedule": crontab(day_of_month="1", hour="0", minute="0"),  # día 1, 00:00
    },
}

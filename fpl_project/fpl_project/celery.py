"""
Celery configuration for FPL project.
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fpl_project.settings')

app = Celery('fpl_project')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from Django apps
app.autodiscover_tasks()

# Celery Beat schedule
app.conf.beat_schedule = {
    'fetch-fpl-data-hourly': {
        'task': 'fpl_app.tasks.fetch_fpl_data_task',
        'schedule': crontab(minute=0),  # Every hour
    },
    'retrain-models-weekly': {
        'task': 'fpl_app.tasks.retrain_model_task',
        'schedule': crontab(day_of_week=0, hour=2, minute=0),  # Sunday 2 AM
    },
    'calculate-metrics-daily': {
        'task': 'fpl_app.tasks.calculate_metrics_task',
        'schedule': crontab(hour=23, minute=0),  # Daily at 11 PM
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

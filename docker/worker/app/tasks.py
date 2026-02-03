"""Climate Data Platform - Celery worker tasks."""

import os
import time

from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery("climate-worker", broker=REDIS_URL, backend=REDIS_URL)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@app.task(bind=True, max_retries=3)
def process_dataset(self, dataset_id: str, variables: list, time_range: dict):
    """Process a climate dataset extraction request."""
    try:
        self.update_state(state="PROCESSING", meta={"dataset": dataset_id})
        # Simulate data processing
        time.sleep(2)
        return {
            "status": "completed",
            "dataset": dataset_id,
            "variables": variables,
            "output_path": f"/data/output/{dataset_id}.nc",
        }
    except Exception as exc:
        self.retry(exc=exc, countdown=60)


@app.task(bind=True)
def aggregate_data(self, dataset_id: str, aggregation: str, spatial_bounds: dict):
    """Aggregate climate data over spatial/temporal dimensions."""
    self.update_state(state="AGGREGATING", meta={"dataset": dataset_id})
    time.sleep(1)
    return {
        "status": "completed",
        "dataset": dataset_id,
        "aggregation": aggregation,
    }


@app.task
def health_check():
    """Worker health check task."""
    return {"status": "healthy", "worker": "celery"}

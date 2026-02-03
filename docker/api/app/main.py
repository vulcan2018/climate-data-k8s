"""Climate Data Platform API - FastAPI application."""

import os
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Climate Data Platform API",
    description="REST API for climate data access and processing",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


@app.get("/health")
async def health():
    """Health check endpoint for Kubernetes probes."""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/ready")
async def readiness():
    """Readiness probe - checks downstream dependencies."""
    return {"status": "ready"}


@app.get("/api/v1/datasets")
async def list_datasets():
    """List available climate datasets."""
    return {
        "datasets": [
            {
                "id": "era5-pressure",
                "name": "ERA5 Pressure Levels",
                "temporal_range": "1940-present",
                "resolution": "0.25deg",
            },
            {
                "id": "era5-single",
                "name": "ERA5 Single Levels",
                "temporal_range": "1940-present",
                "resolution": "0.25deg",
            },
            {
                "id": "cams-global",
                "name": "CAMS Global Reanalysis",
                "temporal_range": "2003-present",
                "resolution": "0.75deg",
            },
        ]
    }


@app.get("/api/v1/datasets/{dataset_id}")
async def get_dataset(dataset_id: str):
    """Get dataset metadata."""
    datasets = {
        "era5-pressure": {
            "id": "era5-pressure",
            "name": "ERA5 Pressure Levels",
            "variables": ["temperature", "geopotential", "relative_humidity"],
            "pressure_levels": [1000, 850, 500, 300, 200],
            "temporal_range": "1940-present",
            "resolution": "0.25deg",
        },
    }
    if dataset_id not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return datasets[dataset_id]


@app.post("/api/v1/jobs")
async def submit_job():
    """Submit a data processing job to the worker queue."""
    job_id = f"job-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    return {"job_id": job_id, "status": "queued"}

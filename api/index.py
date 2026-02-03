"""Climate Data Platform API - Vercel serverless deployment."""

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/v1/datasets")
async def list_datasets():
    return {
        "datasets": [
            {
                "id": "era5-pressure",
                "name": "ERA5 Pressure Levels",
                "temporal_range": "1940-present",
                "resolution": "0.25deg",
                "variables": ["temperature", "geopotential", "relative_humidity", "wind_u", "wind_v"],
            },
            {
                "id": "era5-single",
                "name": "ERA5 Single Levels",
                "temporal_range": "1940-present",
                "resolution": "0.25deg",
                "variables": ["2m_temperature", "surface_pressure", "total_precipitation"],
            },
            {
                "id": "cams-global",
                "name": "CAMS Global Reanalysis",
                "temporal_range": "2003-present",
                "resolution": "0.75deg",
                "variables": ["ozone", "carbon_monoxide", "nitrogen_dioxide"],
            },
            {
                "id": "satellite-soil-moisture",
                "name": "Satellite Soil Moisture",
                "temporal_range": "1978-present",
                "resolution": "0.25deg",
                "variables": ["volumetric_soil_moisture", "soil_moisture_anomaly"],
            },
        ]
    }


@app.get("/api/v1/datasets/{dataset_id}")
async def get_dataset(dataset_id: str):
    datasets = {
        "era5-pressure": {
            "id": "era5-pressure",
            "name": "ERA5 Pressure Levels",
            "description": "Fifth generation atmospheric reanalysis on pressure levels",
            "variables": ["temperature", "geopotential", "relative_humidity", "wind_u", "wind_v"],
            "pressure_levels": [1000, 925, 850, 700, 500, 300, 250, 200, 100, 50],
            "temporal_range": "1940-present",
            "resolution": "0.25deg",
            "format": "NetCDF / GRIB",
            "update_frequency": "Monthly",
        },
        "era5-single": {
            "id": "era5-single",
            "name": "ERA5 Single Levels",
            "description": "Fifth generation atmospheric reanalysis on single levels",
            "variables": ["2m_temperature", "surface_pressure", "total_precipitation", "10m_wind"],
            "temporal_range": "1940-present",
            "resolution": "0.25deg",
            "format": "NetCDF / GRIB",
            "update_frequency": "Monthly",
        },
        "cams-global": {
            "id": "cams-global",
            "name": "CAMS Global Reanalysis",
            "description": "Atmospheric composition reanalysis",
            "variables": ["ozone", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide"],
            "temporal_range": "2003-present",
            "resolution": "0.75deg",
            "format": "NetCDF / GRIB",
            "update_frequency": "Quarterly",
        },
        "satellite-soil-moisture": {
            "id": "satellite-soil-moisture",
            "name": "Satellite Soil Moisture",
            "description": "Multi-satellite soil moisture dataset",
            "variables": ["volumetric_soil_moisture", "soil_moisture_anomaly"],
            "temporal_range": "1978-present",
            "resolution": "0.25deg",
            "format": "NetCDF",
            "update_frequency": "Daily",
        },
    }
    if dataset_id not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return datasets[dataset_id]


@app.post("/api/v1/jobs")
async def submit_job():
    job_id = f"job-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    return {"job_id": job_id, "status": "queued", "message": "Job submitted to processing queue"}


@app.get("/api/v1/status")
async def platform_status():
    return {
        "platform": "Climate Data Platform",
        "version": "1.0.0",
        "status": "operational",
        "services": {
            "api": "healthy",
            "worker": "healthy",
            "broker": "healthy",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

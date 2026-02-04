"""Generate ERA5-like 2m temperature JSON files for the climate data demo.

This script creates realistic temperature grids based on latitude, season,
and land/ocean distribution. The output format matches what a real CDS API
download + NetCDF conversion would produce.

For real data, install: pip install -r requirements-local.txt
and configure ~/.cdsapirc with your CDS API key.

Usage:
    python prepare_data.py           # Generate synthetic data (no deps)
    python prepare_data.py --real    # Download from CDS API (requires cdsapi, netCDF4)
"""

import json
import math
import os
import sys

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "public", "data")

# 2.5 degree grid
LATS = [90.0 - i * 2.5 for i in range(73)]   # 90 to -90
LONS = [-180.0 + i * 2.5 for i in range(144)] # -180 to 177.5


def generate_synthetic(month: int) -> list[list[float]]:
    """Generate realistic 2m temperature grid for a given month.

    Uses a simple model: base temperature from latitude + seasonal shift
    + land/ocean contrast + elevation proxy.
    """
    # Northern hemisphere: month 1 = winter, month 7 = summer
    # Season factor: +1 in July (NH summer), -1 in January (NH winter)
    season = math.cos(math.radians((month - 7) * 30))

    values = []
    for lat in LATS:
        row = []
        for lon in LONS:
            # Base: equator ~300K, poles ~250K
            base = 288.0 - 40.0 * abs(lat) / 90.0

            # Seasonal variation: stronger at high latitudes
            seasonal = season * 15.0 * (abs(lat) / 90.0)
            # Flip sign for southern hemisphere
            if lat < 0:
                seasonal = -seasonal

            # Simple land/ocean contrast (land has bigger seasonal swing)
            # Rough continental mask: more land in NH midlatitudes
            is_land = False
            if -30 < lat < 70:
                # Eurasia
                if 0 < lon < 140 and lat > 10:
                    is_land = True
                # Africa
                if -20 < lon < 50 and -35 < lat < 35:
                    is_land = True
                # North America
                if -130 < lon < -60 and lat > 15:
                    is_land = True
                # South America
                if -80 < lon < -35 and -55 < lat < 10:
                    is_land = True
                # Australia
                if 115 < lon < 155 and -40 < lat < -10:
                    is_land = True

            if is_land:
                seasonal *= 1.4
                base -= 2  # slightly cooler on average

            # Add some zonal variation
            zonal = 3.0 * math.sin(math.radians(lon * 2))

            temp = base + seasonal + zonal

            # Clamp to realistic range
            temp = max(210.0, min(320.0, temp))
            row.append(round(temp, 1))
        values.append(row)
    return values


def download_real(year: int, month: int, day: int, output_path: str):
    """Download real ERA5 data from CDS API and convert to JSON."""
    try:
        import cdsapi
        import netCDF4
        import numpy as np
    except ImportError:
        print("Install dependencies: pip install -r requirements-local.txt")
        sys.exit(1)

    c = cdsapi.Client()
    nc_path = output_path.replace(".json", ".nc")

    c.retrieve(
        "reanalysis-era5-single-levels",
        {
            "product_type": "reanalysis",
            "variable": "2m_temperature",
            "year": str(year),
            "month": f"{month:02d}",
            "day": f"{day:02d}",
            "time": "12:00",
            "grid": "2.5/2.5",
            "format": "netcdf",
        },
        nc_path,
    )

    ds = netCDF4.Dataset(nc_path)
    t2m = ds.variables["t2m"][0, :, :]  # first time step
    lats_nc = ds.variables["latitude"][:]
    lons_nc = ds.variables["longitude"][:]
    ds.close()

    data = {
        "variable": "2m_temperature",
        "units": "K",
        "date": f"{year}-{month:02d}-{day:02d}",
        "time": "12:00",
        "grid": "2.5deg",
        "lats": [float(x) for x in lats_nc],
        "lons": [float(x) for x in lons_nc],
        "values": [[round(float(v), 1) for v in row] for row in t2m],
    }

    with open(output_path, "w") as f:
        json.dump(data, f, separators=(",", ":"))

    os.remove(nc_path)
    print(f"Written: {output_path} ({os.path.getsize(output_path)} bytes)")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    use_real = "--real" in sys.argv

    dates = [
        (2024, 1, 1),
        (2024, 7, 1),
    ]

    for year, month, day in dates:
        filename = f"era5_t2m_{year}{month:02d}{day:02d}.json"
        output_path = os.path.join(OUTPUT_DIR, filename)

        if use_real:
            print(f"Downloading ERA5 data for {year}-{month:02d}-{day:02d}...")
            download_real(year, month, day, output_path)
        else:
            print(f"Generating synthetic data for {year}-{month:02d}-{day:02d}...")
            values = generate_synthetic(month)
            data = {
                "variable": "2m_temperature",
                "units": "K",
                "date": f"{year}-{month:02d}-{day:02d}",
                "time": "12:00",
                "grid": "2.5deg",
                "lats": LATS,
                "lons": LONS,
                "values": values,
            }
            with open(output_path, "w") as f:
                json.dump(data, f, separators=(",", ":"))
            size = os.path.getsize(output_path)
            print(f"Written: {filename} ({size:,} bytes)")


if __name__ == "__main__":
    main()

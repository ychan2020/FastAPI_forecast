# file: main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import httpx   # async HTTP client (pip install httpx)
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Open-Meteo Forecast Proxy with Geocoding",
    description="FastAPI wrapper around Open-Meteo weather API + Nominatim geocoding",
    version="0.2.0",
)


class GeocodeParams(BaseModel):
    """Query parameters for geocoding."""
    q: str  # e.g., "Berlin, Germany"
    format: str = "json"  # Fixed to JSON
    limit: int = 1  # Return only the top result


class ForecastParams(BaseModel):
    """Query parameters that mirror the Open-Meteo endpoint, with optional geocoding."""
    location: Optional[str] = None       # e.g., "Berlin" – will auto-geocode if provided
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    current: Optional[str] = None        # e.g., "temperature_2m,wind_speed_10m"
    hourly: Optional[str] = None         # e.g., "temperature_2m,relative_humidity_2m"


@app.get("/geocode", response_class=JSONResponse)
async def get_geocode(
    q: str = Query(..., description="Location to search for"),
    limit: int = Query(1, ge=1, le=10, description="Number of results to return")
):
    """
    Geocode a location name to lat/lon using Nominatim (OpenStreetMap).
    Returns the top result(s) as JSON.
    """
    if not q.strip():
        raise HTTPException(status_code=400, detail="Location query 'q' is required")

    params = {
        "q": q,
        "format": "json",
        "limit": limit,
        "addressdetails": 1,
    }

    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "FastAPI-Weather-Proxy/0.2.0 (your.email@example.com)"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Nominatim error: {exc.response.text}"
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Network error: {exc}")

    data = resp.json()
    if not data:
        raise HTTPException(status_code=404, detail=f"No results found for location: {q}")

    return JSONResponse(content=data)


@app.get("/forecast", response_class=JSONResponse)
async def get_forecast(
    location: Optional[str] = Query(None, description="City name or address to geocode"),
    latitude: Optional[float] = Query(None, description="Latitude (if location not used)"),
    longitude: Optional[float] = Query(None, description="Longitude (if location not used)"),
    current: Optional[str] = Query(None, description="Comma-separated current weather variables"),
    hourly: Optional[str] = Query(None, description="Comma-separated hourly variables"),
):
    """
    Proxy the request to Open-Meteo. 
    - If `location` is provided → auto-geocode to lat/lon.
    - Else, require both `latitude` and `longitude`.
    """
    lat = None
    lon = None

    # Case 1: Use location → geocode
    if location:
        geocode_params = {
            "q": location,
            "format": "json",
            "limit": 1,
            "addressdetails": 1,
        }
        geocode_url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "FastAPI-Weather-Proxy/0.2.0"}

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(geocode_url, params=geocode_params, headers=headers)
                resp.raise_for_status()
                geocode_data = resp.json()

                if not geocode_data:
                    raise HTTPException(status_code=404, detail=f"No geocoding results for: {location}")

                lat = float(geocode_data[0]["lat"])
                lon = float(geocode_data[0]["lon"])

            except (httpx.HTTPStatusError, ValueError) as exc:
                raise HTTPException(status_code=502, detail=f"Geocoding failed: {str(exc)}")

    # Case 2: Use explicit latitude/longitude
    elif latitude is not None and longitude is not None:
        lat = latitude
        lon = longitude
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide either 'location' or both 'latitude' and 'longitude'"
        )

    # Build Open-Meteo request
    params: dict[str, str | float] = {
        "latitude": lat,
        "longitude": lon,
    }
    if current:
        params["current"] = current
    if hourly:
        params["hourly"] = hourly

    url = "https://api.open-meteo.com/v1/forecast"

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Open-Meteo error: {exc.response.text}"
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Network error: {exc}")

    return JSONResponse(content=resp.json())
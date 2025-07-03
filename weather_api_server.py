#!/usr/bin/env python3
"""
Simplified Weather API Server for Smart Building Assistant
Provides real-time weather data using Open-Meteo API
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weather-api-server")

class WeatherRequest(BaseModel):
    location: str
    units: str = "metric"
    include_forecast: bool = False

class WeatherService:
    """Simple weather service using Open-Meteo API"""
    
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1"
        self.university_coords = {
            "latitude": 11.052754371982356,
            "longitude": 106.666777616965,
            "name": "Đại học quốc tế Miền Đông",
            "timezone": "Asia/Ho_Chi_Minh"
        }
        self.client = None
        
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def get_weather_data(self, latitude: float, longitude: float, 
                             location_name: str = "Unknown") -> Dict[str, Any]:
        """Get current weather data from Open-Meteo API"""
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m", 
                    "apparent_temperature",
                    "weather_code",
                    "surface_pressure",
                    "wind_speed_10m",
                    "wind_direction_10m"
                ],
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "weather_code",
                    "precipitation_sum"
                ],
                "timezone": "Asia/Ho_Chi_Minh",
                "forecast_days": 3
            }
            
            response = await self.client.get(f"{self.base_url}/forecast", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Process current weather
            current = data.get("current", {})
            current_weather = {
                "location": location_name,
                "coordinates": f"{latitude}, {longitude}",
                "timestamp": current.get("time"),
                "temperature": current.get("temperature_2m"),
                "feels_like": current.get("apparent_temperature"),
                "humidity": current.get("relative_humidity_2m"),
                "pressure": current.get("surface_pressure"),
                "wind_speed": current.get("wind_speed_10m"),
                "wind_direction": current.get("wind_direction_10m"),
                "weather_code": current.get("weather_code"),
                "condition": self.get_weather_condition(current.get("weather_code", 0))
            }
            
            # Process daily forecast
            daily = data.get("daily", {})
            daily_forecast = []
            if daily.get("time"):
                for i in range(min(3, len(daily["time"]))):
                    daily_forecast.append({
                        "date": daily["time"][i],
                        "max_temp": daily.get("temperature_2m_max", [])[i] if i < len(daily.get("temperature_2m_max", [])) else None,
                        "min_temp": daily.get("temperature_2m_min", [])[i] if i < len(daily.get("temperature_2m_min", [])) else None,
                        "weather_code": daily.get("weather_code", [])[i] if i < len(daily.get("weather_code", [])) else None,
                        "precipitation": daily.get("precipitation_sum", [])[i] if i < len(daily.get("precipitation_sum", [])) else None,
                        "condition": self.get_weather_condition(daily.get("weather_code", [])[i] if i < len(daily.get("weather_code", [])) else 0)
                    })
            
            return {
                "current": current_weather,
                "daily_forecast": daily_forecast,
                "timezone": data.get("timezone"),
                "elevation": data.get("elevation"),
                "api_source": "Open-Meteo"
            }
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return {
                "error": str(e),
                "location": location_name,
                "coordinates": f"{latitude}, {longitude}",
                "api_source": "Open-Meteo"
            }

    def get_weather_condition(self, weather_code: int) -> str:
        """Convert WMO weather code to human-readable condition"""
        code_map = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy", 
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return code_map.get(weather_code, f"Unknown weather (code: {weather_code})")

    async def get_university_weather(self) -> Dict[str, Any]:
        """Get weather for the university location"""
        return await self.get_weather_data(
            self.university_coords["latitude"],
            self.university_coords["longitude"],
            self.university_coords["name"]
        )

    async def get_location_coordinates(self, location_name: str) -> Optional[Dict[str, Any]]:
        """Get coordinates for a location using Open-Meteo Geocoding API"""
        try:
            params = {
                "name": location_name,
                "count": 1,
                "language": "en",
                "format": "json"
            }
            
            response = await self.client.get("https://geocoding-api.open-meteo.com/v1/search", params=params)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            if results:
                result = results[0]
                return {
                    "latitude": result.get("latitude"),
                    "longitude": result.get("longitude"),
                    "name": result.get("name"),
                    "country": result.get("country"),
                    "admin1": result.get("admin1")
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error geocoding location {location_name}: {e}")
            return None

# FastAPI app
app = FastAPI(title="Weather API Server", version="1.0.0")

# Global weather service instance
weather_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize the weather service on startup"""
    global weather_service
    weather_service = WeatherService()
    await weather_service.__aenter__()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global weather_service
    if weather_service:
        await weather_service.__aexit__(None, None, None)

@app.post("/weather")
async def get_weather(request: WeatherRequest):
    """Get weather data for a location"""
    try:
        global weather_service
        if not weather_service:
            raise HTTPException(status_code=500, detail="Service not initialized")
        
        location = request.location.strip().lower()
        
        # Handle special cases
        if location in ["university", "đại học quốc tế miền đông", "current location"]:
            weather_data = await weather_service.get_university_weather()
        else:
            # Get coordinates for the location
            coords = await weather_service.get_location_coordinates(request.location)
            if coords:
                weather_data = await weather_service.get_weather_data(
                    coords["latitude"],
                    coords["longitude"],
                    coords["name"]
                )
            else:
                raise HTTPException(status_code=404, detail=f"Location not found: {request.location}")
        
        # Return forecast or current weather based on request
        if request.include_forecast:
            return JSONResponse(content=weather_data)
        else:
            return JSONResponse(content=weather_data.get("current", {}))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weather/university")
async def get_university_weather():
    """Get weather data for the university location"""
    try:
        global weather_service
        if not weather_service:
            raise HTTPException(status_code=500, detail="Service not initialized")
        
        weather_data = await weather_service.get_university_weather()
        return JSONResponse(content=weather_data)
        
    except Exception as e:
        logger.error(f"Error getting university weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "service": "Weather API Server"
    }

async def run_server():
    """Run the weather API server"""
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    print("Starting Weather API Server on port 8001...")
    asyncio.run(run_server())

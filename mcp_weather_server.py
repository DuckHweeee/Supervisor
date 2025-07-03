#!/usr/bin/env python3
"""
MCP Server for Open-Meteo Weather API Integration
Following Model Context Protocol specifications from https://modelcontextprotocol.io/
Provides real-time weather data for the Smart Building AI Assistant
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, Sequence
from datetime import datetime, timedelta
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,
    Tool,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
    CallToolResult,
    ListResourcesResult,
    ListToolsResult,
    ReadResourceResult,
    ListPromptsResult,
    GetPromptResult
)
import mcp.server.stdio
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weather-mcp-server")

# FastAPI models for HTTP requests
class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]

class ToolCallResponse(BaseModel):
    content: List[Dict[str, Any]]

class WeatherMCPServer:
    """
    MCP Server for weather data following Model Context Protocol specifications
    
    This server provides:
    - Resources: Static weather data endpoints
    - Tools: Interactive weather functions
    - Prompts: Pre-defined weather queries
    """
    def __init__(self):
        self.server = Server("weather-mcp-server")
        self.base_url = "https://api.open-meteo.com/v1"
        self.university_coords = {
            "latitude": 11.052754371982356,
            "longitude": 106.666777616965,
            "name": "Đại học quốc tế Miền Đông",
            "timezone": "Asia/Ho_Chi_Minh"
        }
        self.client = None
        
        # MCP Server capabilities
        self.capabilities = {
            "resources": {},
            "tools": {},
            "prompts": {}
        }
        
    async def __aenter__(self):
        self.client = httpx.AsyncClient()
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
                "hourly": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "weather_code"
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
                "elevation": data.get("elevation")
            }
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return {
                "error": str(e),
                "location": location_name,
                "coordinates": f"{latitude}, {longitude}"
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

    async def get_location_coordinates(self, location_name: str) -> Optional[Dict[str, float]]:
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

    def setup_handlers(self):
        """Setup MCP server handlers following official protocol specifications"""
        
        # Resources: Provide structured data endpoints
        @self.server.list_resources()
        async def handle_list_resources() -> ListResourcesResult:
            """
            List available weather resources
            Resources in MCP represent data that can be read by the client
            """
            return ListResourcesResult(
                resources=[
                    Resource(
                        uri="weather://university/current",
                        name="University Current Weather",
                        description="Real-time weather data for Đại học quốc tế Miền Đông",
                        mimeType="application/json"
                    ),
                    Resource(
                        uri="weather://university/forecast",
                        name="University Weather Forecast", 
                        description="3-day weather forecast for the university location",
                        mimeType="application/json"
                    ),
                    Resource(
                        uri="weather://university/hvac-data",
                        name="HVAC Weather Integration",
                        description="Weather data formatted for smart building HVAC systems",
                        mimeType="application/json"
                    ),
                    Resource(
                        uri="weather://university/energy-data",
                        name="Energy Management Weather Data",
                        description="Weather metrics relevant to building energy management",
                        mimeType="application/json"
                    )
                ]
            )

        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> ReadResourceResult:
            """
            Read weather resource data
            Provides the actual content of a resource identified by URI
            """
            try:
                if uri == "weather://university/current":
                    weather_data = await self.get_university_weather()
                    current = weather_data.get("current", {})
                    
                    # Format for MCP consumption
                    resource_data = {
                        "type": "current_weather",
                        "location": self.university_coords["name"],
                        "coordinates": f"{self.university_coords['latitude']}, {self.university_coords['longitude']}",
                        "timestamp": datetime.now().isoformat(),
                        "data": current,
                        "source": "Open-Meteo API"
                    }
                    
                    return ReadResourceResult(
                        contents=[
                            TextContent(
                                type="text",
                                text=json.dumps(resource_data, indent=2, ensure_ascii=False)
                            )
                        ]
                    )
                
                elif uri == "weather://university/forecast":
                    weather_data = await self.get_university_weather()
                    forecast = weather_data.get("daily_forecast", [])
                    
                    resource_data = {
                        "type": "weather_forecast",
                        "location": self.university_coords["name"],
                        "forecast_days": len(forecast),
                        "data": forecast,
                        "generated_at": datetime.now().isoformat()
                    }
                    
                    return ReadResourceResult(
                        contents=[
                            TextContent(
                                type="text",
                                text=json.dumps(resource_data, indent=2, ensure_ascii=False)
                            )
                        ]
                    )
                
                elif uri == "weather://university/hvac-data":
                    weather_data = await self.get_university_weather()
                    current = weather_data.get("current", {})
                    
                    hvac_data = {
                        "type": "hvac_weather_integration",
                        "location": self.university_coords["name"],
                        "outdoor_temperature": current.get("temperature"),
                        "outdoor_humidity": current.get("humidity"),
                        "outdoor_pressure": current.get("pressure"),
                        "wind_speed": current.get("wind_speed"),
                        "weather_condition": current.get("condition"),
                        "hvac_recommendations": self.get_hvac_recommendations(current),
                        "optimal_setpoints": self.calculate_optimal_setpoints(current),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    return ReadResourceResult(
                        contents=[
                            TextContent(
                                type="text",
                                text=json.dumps(hvac_data, indent=2, ensure_ascii=False)
                            )
                        ]
                    )
                
                elif uri == "weather://university/energy-data":
                    weather_data = await self.get_university_weather()
                    current = weather_data.get("current", {})
                    
                    energy_data = {
                        "type": "energy_weather_data",
                        "location": self.university_coords["name"],
                        "cooling_load_factor": self.calculate_cooling_load_factor(current),
                        "natural_lighting_potential": self.assess_natural_lighting(current),
                        "ventilation_recommendations": self.get_ventilation_recommendations(current),
                        "energy_efficiency_tips": self.get_energy_recommendations(current),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    return ReadResourceResult(
                        contents=[
                            TextContent(
                                type="text",
                                text=json.dumps(energy_data, indent=2, ensure_ascii=False)
                            )
                        ]
                    )
                
                else:
                    raise ValueError(f"Unknown resource URI: {uri}")
                    
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                error_data = {
                    "error": str(e),
                    "uri": uri,
                    "timestamp": datetime.now().isoformat()
                }
                
                return ReadResourceResult(
                    contents=[
                        TextContent(
                            type="text",
                            text=json.dumps(error_data, indent=2)
                        )
                    ]
                )

        # Tools: Provide interactive functions that can be called
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """
            List available weather tools
            Tools in MCP are functions that can be called by the client
            """
            return ListToolsResult(
                tools=[
                    Tool(
                        name="get_current_weather",
                        description="Get current weather conditions for any location worldwide",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "Location name, address, or coordinates. Use 'university' for Đại học quốc tế Miền Đông"
                                },
                                "units": {
                                    "type": "string",
                                    "enum": ["metric", "imperial"],
                                    "default": "metric",
                                    "description": "Temperature units (metric=Celsius, imperial=Fahrenheit)"
                                },
                                "include_forecast": {
                                    "type": "boolean",
                                    "default": False,
                                    "description": "Include 3-day weather forecast"
                                },
                                "include_hourly": {
                                    "type": "boolean", 
                                    "default": False,
                                    "description": "Include hourly forecast for today"
                                }
                            },
                            "required": ["location"]
                        }
                    ),
                    Tool(
                        name="get_weather_by_coordinates",
                        description="Get weather data using precise latitude and longitude coordinates",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "latitude": {
                                    "type": "number",
                                    "minimum": -90,
                                    "maximum": 90,
                                    "description": "Latitude coordinate (-90 to 90)"
                                },
                                "longitude": {
                                    "type": "number",
                                    "minimum": -180,
                                    "maximum": 180,
                                    "description": "Longitude coordinate (-180 to 180)"
                                },
                                "location_name": {
                                    "type": "string",
                                    "default": "Custom Location",
                                    "description": "Optional descriptive name for the location"
                                }
                            },
                            "required": ["latitude", "longitude"]
                        }
                    ),
                    Tool(
                        name="get_building_weather_analysis",
                        description="Comprehensive weather analysis for smart building management and HVAC optimization",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "analysis_type": {
                                    "type": "string",
                                    "enum": ["hvac", "energy", "comfort", "comprehensive"],
                                    "default": "comprehensive",
                                    "description": "Type of building analysis to perform"
                                },
                                "include_recommendations": {
                                    "type": "boolean",
                                    "default": True,
                                    "description": "Include actionable recommendations"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="compare_weather_locations",
                        description="Compare weather conditions between multiple locations",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "locations": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "minItems": 2,
                                    "maxItems": 5,
                                    "description": "List of location names to compare"
                                },
                                "metrics": {
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "enum": ["temperature", "humidity", "pressure", "wind", "condition"]
                                    },
                                    "default": ["temperature", "humidity", "condition"],
                                    "description": "Weather metrics to compare"
                                }
                            },
                            "required": ["locations"]
                        }
                    ),
                    Tool(
                        name="get_weather_alerts",
                        description="Check for weather alerts and warnings for the university location",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "severity_level": {
                                    "type": "string",
                                    "enum": ["all", "minor", "moderate", "severe"],
                                    "default": "all",
                                    "description": "Minimum severity level for alerts"
                                }
                            }
                        }
                    )
                ]
            )

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> CallToolResult:
            """Handle tool calls with proper MCP protocol responses"""
            try:
                if name == "get_current_weather":
                    location = arguments.get("location", "").strip()
                    include_forecast = arguments.get("include_forecast", False)
                    
                    # Handle special case for university
                    if location.lower() in ["university", "đại học quốc tế miền đông", "current location"]:
                        weather_data = await self.get_university_weather()
                    else:
                        # Get coordinates for the location
                        coords = await self.get_location_coordinates(location)
                        if coords:
                            weather_data = await self.get_weather_data(
                                coords["latitude"],
                                coords["longitude"],
                                coords["name"]
                            )
                        else:
                            return CallToolResult(
                                content=[
                                    TextContent(
                                        type="text",
                                        text=f"Could not find location: {location}"
                                    )
                                ]
                            )
                    
                    if include_forecast:
                        result = json.dumps(weather_data, indent=2, ensure_ascii=False)
                    else:
                        result = json.dumps(weather_data.get("current", {}), indent=2, ensure_ascii=False)
                    
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=result
                            )
                        ]
                    )
                
                elif name == "get_weather_by_coordinates":
                    latitude = arguments.get("latitude")
                    longitude = arguments.get("longitude")
                    location_name = arguments.get("location_name", "Unknown Location")
                    
                    weather_data = await self.get_weather_data(latitude, longitude, location_name)
                    result = json.dumps(weather_data, indent=2, ensure_ascii=False)
                    
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=result
                            )
                        ]
                    )
                
                elif name == "get_building_weather_analysis":
                    analysis_type = arguments.get("analysis_type", "comprehensive")
                    include_recommendations = arguments.get("include_recommendations", True)
                    
                    weather_data = await self.get_university_weather()
                    current = weather_data.get("current", {})
                    
                    if analysis_type == "hvac":
                        analysis_data = {
                            "type": "hvac_analysis",
                            "location": self.university_coords["name"],
                            "outdoor_conditions": current,
                            "hvac_recommendations": self.get_hvac_recommendations(current) if include_recommendations else [],
                            "optimal_setpoints": self.calculate_optimal_setpoints(current),
                            "timestamp": datetime.now().isoformat()
                        }
                    elif analysis_type == "energy":
                        analysis_data = {
                            "type": "energy_analysis",
                            "location": self.university_coords["name"],
                            "weather_conditions": current,
                            "energy_recommendations": self.get_energy_recommendations(current) if include_recommendations else [],
                            "cooling_load_factor": self.calculate_cooling_load_factor(current),
                            "natural_lighting_potential": self.assess_natural_lighting(current),
                            "timestamp": datetime.now().isoformat()
                        }
                    elif analysis_type == "comfort":
                        analysis_data = {
                            "type": "comfort_analysis",
                            "location": self.university_coords["name"],
                            "weather_conditions": current,
                            "comfort_recommendations": self.get_comfort_recommendations(current) if include_recommendations else [],
                            "thermal_comfort_index": self.calculate_thermal_comfort(current),
                            "timestamp": datetime.now().isoformat()
                        }
                    else:  # comprehensive
                        analysis_data = {
                            "type": "comprehensive_analysis",
                            "location": self.university_coords["name"],
                            "current_conditions": current,
                            "forecast": weather_data.get("daily_forecast", [])[:3],
                            "hvac_recommendations": self.get_hvac_recommendations(current) if include_recommendations else [],
                            "energy_recommendations": self.get_energy_recommendations(current) if include_recommendations else [],
                            "comfort_recommendations": self.get_comfort_recommendations(current) if include_recommendations else [],
                            "building_insights": self.get_building_insights(current),
                            "timestamp": datetime.now().isoformat()
                        }
                    
                    result = json.dumps(analysis_data, indent=2, ensure_ascii=False)
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=result
                            )
                        ]
                    )
                
                elif name == "compare_weather_locations":
                    locations = arguments.get("locations", [])
                    metrics = arguments.get("metrics", ["temperature", "humidity", "condition"])
                    
                    if len(locations) < 2:
                        return CallToolResult(
                            content=[
                                TextContent(
                                    type="text",
                                    text="Please provide at least 2 locations to compare"
                                )
                            ]
                        )
                    
                    comparison_data = {
                        "type": "weather_comparison",
                        "locations": [],
                        "metrics": metrics,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    for location in locations:
                        if location.lower() in ["university", "đại học quốc tế miền đông"]:
                            weather_data = await self.get_university_weather()
                        else:
                            coords = await self.get_location_coordinates(location)
                            if coords:
                                weather_data = await self.get_weather_data(
                                    coords["latitude"],
                                    coords["longitude"],
                                    coords["name"]
                                )
                            else:
                                weather_data = {"error": f"Could not find location: {location}"}
                        
                        comparison_data["locations"].append({
                            "name": location,
                            "weather_data": weather_data.get("current", {})
                        })
                    
                    result = json.dumps(comparison_data, indent=2, ensure_ascii=False)
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=result
                            )
                        ]
                    )
                
                elif name == "get_weather_alerts":
                    severity_level = arguments.get("severity_level", "all")
                    
                    # For now, provide basic weather alerts based on conditions
                    weather_data = await self.get_university_weather()
                    current = weather_data.get("current", {})
                    
                    alerts = []
                    temp = current.get("temperature")
                    humidity = current.get("humidity")
                    wind_speed = current.get("wind_speed")
                    
                    if temp is not None:
                        if temp > 35:
                            alerts.append({
                                "severity": "severe",
                                "type": "heat_warning",
                                "message": f"Extreme heat warning: {temp}°C",
                                "recommendation": "Take precautions for heat exposure"
                            })
                        elif temp > 30:
                            alerts.append({
                                "severity": "moderate",
                                "type": "heat_advisory",
                                "message": f"High temperature: {temp}°C",
                                "recommendation": "Stay hydrated and avoid prolonged outdoor activities"
                            })
                    
                    if humidity is not None and humidity > 80:
                        alerts.append({
                            "severity": "minor",
                            "type": "humidity_advisory",
                            "message": f"High humidity: {humidity}%",
                            "recommendation": "Consider using dehumidifiers in buildings"
                        })
                    
                    if wind_speed is not None and wind_speed > 50:
                        alerts.append({
                            "severity": "moderate",
                            "type": "wind_advisory",
                            "message": f"Strong winds: {wind_speed} km/h",
                            "recommendation": "Secure outdoor objects and exercise caution"
                        })
                    
                    # Filter by severity level
                    if severity_level != "all":
                        severity_order = {"minor": 1, "moderate": 2, "severe": 3}
                        min_severity = severity_order.get(severity_level, 0)
                        alerts = [alert for alert in alerts if severity_order.get(alert["severity"], 0) >= min_severity]
                    
                    alert_data = {
                        "type": "weather_alerts",
                        "location": self.university_coords["name"],
                        "severity_filter": severity_level,
                        "alerts": alerts,
                        "alert_count": len(alerts),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    result = json.dumps(alert_data, indent=2, ensure_ascii=False)
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=result
                            )
                        ]
                    )
                
                else:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Unknown tool: {name}"
                            )
                        ]
                    )
                    
            except Exception as e:
                logger.error(f"Error handling tool call {name}: {e}")
                return CallToolResult(
                    isError=True,
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error: {str(e)}"
                        )
                    ]
                )

        # Prompts: Provide reusable prompt templates
        @self.server.list_prompts()
        async def handle_list_prompts() -> ListPromptsResult:
            """
            List available weather prompts
            Prompts in MCP are reusable templates for common tasks
            """
            return ListPromptsResult(
                prompts=[
                    Prompt(
                        name="weather_report",
                        description="Generate a comprehensive weather report for smart building management",
                        arguments=[
                            PromptArgument(
                                name="location",
                                description="Location name (default: university)",
                                required=False
                            ),
                            PromptArgument(
                                name="include_forecast",
                                description="Include weather forecast (true/false)",
                                required=False
                            )
                        ]
                    ),
                    Prompt(
                        name="hvac_optimization",
                        description="Generate HVAC optimization recommendations based on current weather",
                        arguments=[
                            PromptArgument(
                                name="building_type",
                                description="Type of building (office, university, residential)",
                                required=False
                            )
                        ]
                    ),
                    Prompt(
                        name="energy_efficiency",
                        description="Generate energy efficiency recommendations based on weather conditions",
                        arguments=[
                            PromptArgument(
                                name="focus_area",
                                description="Focus area (cooling, heating, lighting, ventilation)",
                                required=False
                            )
                        ]
                    ),
                    Prompt(
                        name="weather_comparison",
                        description="Compare weather conditions between multiple locations",
                        arguments=[
                            PromptArgument(
                                name="locations",
                                description="Comma-separated list of locations to compare",
                                required=True
                            )
                        ]
                    )
                ]
            )

        @self.server.get_prompt()
        async def handle_get_prompt(name: str, arguments: dict) -> GetPromptResult:
            """Handle prompt requests with dynamic content"""
            try:
                if name == "weather_report":
                    location = arguments.get("location", "university")
                    include_forecast = arguments.get("include_forecast", "true").lower() == "true"
                    
                    # Get weather data
                    if location.lower() in ["university", "đại học quốc tế miền đông"]:
                        weather_data = await self.get_university_weather()
                        location_name = self.university_coords["name"]
                    else:
                        coords = await self.get_location_coordinates(location)
                        if coords:
                            weather_data = await self.get_weather_data(
                                coords["latitude"],
                                coords["longitude"],
                                coords["name"]
                            )
                            location_name = coords["name"]
                        else:
                            location_name = location
                            weather_data = {"error": f"Could not find location: {location}"}
                    
                    # Create prompt with embedded weather data
                    prompt_text = f"""Generate a comprehensive weather report for {location_name} suitable for smart building management.

Current Weather Data:
{json.dumps(weather_data.get('current', {}), indent=2, ensure_ascii=False)}
"""
                    
                    if include_forecast and "daily_forecast" in weather_data:
                        prompt_text += f"""
Forecast Data:
{json.dumps(weather_data.get('daily_forecast', []), indent=2, ensure_ascii=False)}
"""
                    
                    prompt_text += """
Please provide:
1. Current conditions summary
2. HVAC system recommendations
3. Energy efficiency suggestions
4. Comfort optimization tips
5. Any weather-related alerts or considerations
"""
                    
                    return GetPromptResult(
                        description=f"Weather report for {location_name}",
                        messages=[
                            PromptMessage(
                                role="user",
                                content=TextContent(
                                    type="text",
                                    text=prompt_text
                                )
                            )
                        ]
                    )
                
                elif name == "hvac_optimization":
                    building_type = arguments.get("building_type", "university")
                    
                    weather_data = await self.get_university_weather()
                    current = weather_data.get("current", {})
                    
                    prompt_text = f"""Optimize HVAC system settings for a {building_type} building based on current weather conditions.

Current Weather:
- Temperature: {current.get('temperature', 'N/A')}°C
- Humidity: {current.get('humidity', 'N/A')}%
- Feels Like: {current.get('feels_like', 'N/A')}°C
- Condition: {current.get('condition', 'Unknown')}
- Wind Speed: {current.get('wind_speed', 'N/A')} km/h

HVAC Recommendations:
{json.dumps(self.get_hvac_recommendations(current), indent=2, ensure_ascii=False)}

Please provide:
1. Optimal temperature setpoints
2. Humidity control strategies
3. Ventilation recommendations
4. Energy-saving opportunities
5. Comfort considerations
"""
                    
                    return GetPromptResult(
                        description=f"HVAC optimization for {building_type}",
                        messages=[
                            PromptMessage(
                                role="user",
                                content=TextContent(
                                    type="text",
                                    text=prompt_text
                                )
                            )
                        ]
                    )
                
                elif name == "energy_efficiency":
                    focus_area = arguments.get("focus_area", "comprehensive")
                    
                    weather_data = await self.get_university_weather()
                    current = weather_data.get("current", {})
                    
                    prompt_text = f"""Provide energy efficiency recommendations focusing on {focus_area} based on current weather conditions.

Current Weather:
{json.dumps(current, indent=2, ensure_ascii=False)}

Energy Recommendations:
{json.dumps(self.get_energy_recommendations(current), indent=2, ensure_ascii=False)}

Please analyze:
1. Current weather impact on energy consumption
2. Optimization opportunities for {focus_area}
3. Cost-saving strategies
4. Sustainability considerations
5. Implementation priorities
"""
                    
                    return GetPromptResult(
                        description=f"Energy efficiency analysis - {focus_area}",
                        messages=[
                            PromptMessage(
                                role="user",
                                content=TextContent(
                                    type="text",
                                    text=prompt_text
                                )
                            )
                        ]
                    )
                
                elif name == "weather_comparison":
                    locations_str = arguments.get("locations", "")
                    locations = [loc.strip() for loc in locations_str.split(",") if loc.strip()]
                    
                    if not locations:
                        return GetPromptResult(
                            description="Weather comparison error",
                            messages=[
                                PromptMessage(
                                    role="user",
                                    content=TextContent(
                                        type="text",
                                        text="Please provide locations to compare (comma-separated)"
                                    )
                                )
                            ]
                        )
                    
                    comparison_data = []
                    for location in locations:
                        if location.lower() in ["university", "đại học quốc tế miền đông"]:
                            weather_data = await self.get_university_weather()
                            location_name = self.university_coords["name"]
                        else:
                            coords = await self.get_location_coordinates(location)
                            if coords:
                                weather_data = await self.get_weather_data(
                                    coords["latitude"],
                                    coords["longitude"],
                                    coords["name"]
                                )
                                location_name = coords["name"]
                            else:
                                location_name = location
                                weather_data = {"error": f"Could not find location: {location}"}
                        
                        comparison_data.append({
                            "location": location_name,
                            "weather": weather_data.get("current", {})
                        })
                    
                    prompt_text = f"""Compare weather conditions between the following locations:

{json.dumps(comparison_data, indent=2, ensure_ascii=False)}

Please provide:
1. Key differences in weather conditions
2. Implications for building management
3. Location-specific recommendations
4. Comparative analysis of energy requirements
5. Comfort considerations for each location
"""
                    
                    return GetPromptResult(
                        description="Weather comparison analysis",
                        messages=[
                            PromptMessage(
                                role="user",
                                content=TextContent(
                                    type="text",
                                    text=prompt_text
                                )
                            )
                        ]
                    )
                
                else:
                    raise ValueError(f"Unknown prompt: {name}")
                    
            except Exception as e:
                logger.error(f"Error handling prompt {name}: {e}")
                return GetPromptResult(
                    description=f"Error in prompt {name}",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text=f"Error generating prompt: {str(e)}"
                            )
                        )
                    ]
                )

    def calculate_optimal_setpoints(self, current_weather: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal HVAC setpoints based on weather"""
        temp = current_weather.get("temperature")
        humidity = current_weather.get("humidity")
        
        setpoints = {
            "cooling_setpoint": 24,  # Default
            "heating_setpoint": 20,  # Default
            "humidity_setpoint": 50,  # Default
            "ventilation_rate": "normal"
        }
        
        if temp is not None:
            if temp > 30:
                setpoints["cooling_setpoint"] = 22
                setpoints["ventilation_rate"] = "high"
            elif temp < 20:
                setpoints["heating_setpoint"] = 22
                setpoints["ventilation_rate"] = "low"
        
        if humidity is not None:
            if humidity > 70:
                setpoints["humidity_setpoint"] = 45
            elif humidity < 40:
                setpoints["humidity_setpoint"] = 55
        
        return setpoints

    def calculate_cooling_load_factor(self, current_weather: Dict[str, Any]) -> float:
        """Calculate cooling load factor based on weather"""
        temp = current_weather.get("temperature", 25)
        humidity = current_weather.get("humidity", 50)
        
        # Simple cooling load calculation
        base_load = max(0, (temp - 20) / 15)  # 0-1 scale
        humidity_factor = max(0, (humidity - 40) / 40)  # 0-1 scale
        
        return min(1.0, base_load + (humidity_factor * 0.3))

    def assess_natural_lighting(self, current_weather: Dict[str, Any]) -> Dict[str, Any]:
        """Assess natural lighting potential"""
        condition = current_weather.get("condition", "").lower()
        
        if "clear" in condition or "sunny" in condition:
            potential = "excellent"
            artificial_lighting_reduction = 80
        elif "partly cloudy" in condition or "mainly clear" in condition:
            potential = "good"
            artificial_lighting_reduction = 50
        elif "cloudy" in condition or "overcast" in condition:
            potential = "moderate"
            artificial_lighting_reduction = 20
        else:
            potential = "poor"
            artificial_lighting_reduction = 0
        
        return {
            "potential": potential,
            "artificial_lighting_reduction": artificial_lighting_reduction,
            "recommendation": f"Reduce artificial lighting by {artificial_lighting_reduction}%"
        }

    def get_ventilation_recommendations(self, current_weather: Dict[str, Any]) -> List[str]:
        """Generate ventilation recommendations"""
        recommendations = []
        temp = current_weather.get("temperature")
        humidity = current_weather.get("humidity")
        wind_speed = current_weather.get("wind_speed")
        
        if temp is not None:
            if 20 <= temp <= 26:
                recommendations.append("Good conditions for natural ventilation")
            elif temp > 26:
                recommendations.append("Consider mechanical ventilation for cooling")
            else:
                recommendations.append("Reduce ventilation to conserve heat")
        
        if humidity is not None:
            if humidity > 70:
                recommendations.append("Increase ventilation to reduce humidity")
            elif humidity < 40:
                recommendations.append("Reduce ventilation to maintain humidity")
        
        if wind_speed is not None and wind_speed > 20:
            recommendations.append("Strong winds - adjust ventilation controls")
        
        return recommendations

    def get_comfort_recommendations(self, current_weather: Dict[str, Any]) -> List[str]:
        """Generate comfort recommendations"""
        recommendations = []
        temp = current_weather.get("temperature")
        humidity = current_weather.get("humidity")
        
        if temp is not None and humidity is not None:
            comfort_index = self.calculate_thermal_comfort(current_weather)
            
            if comfort_index < 0.3:
                recommendations.append("Poor comfort conditions - adjust HVAC settings")
            elif comfort_index < 0.7:
                recommendations.append("Moderate comfort - fine-tune temperature and humidity")
            else:
                recommendations.append("Good comfort conditions - maintain current settings")
        
        return recommendations

    def calculate_thermal_comfort(self, current_weather: Dict[str, Any]) -> float:
        """Calculate thermal comfort index (0-1 scale)"""
        temp = current_weather.get("temperature", 25)
        humidity = current_weather.get("humidity", 50)
        
        # Simplified comfort calculation
        temp_comfort = 1.0 - abs(temp - 24) / 10  # Optimal at 24°C
        humidity_comfort = 1.0 - abs(humidity - 50) / 40  # Optimal at 50%
        
        return max(0, min(1, (temp_comfort + humidity_comfort) / 2))

    def get_building_insights(self, current_weather: Dict[str, Any]) -> Dict[str, Any]:
        """Generate building management insights"""
        temp = current_weather.get("temperature")
        humidity = current_weather.get("humidity")
        condition = current_weather.get("condition", "")
        
        insights = {
            "energy_efficiency_score": self.calculate_energy_efficiency_score(current_weather),
            "comfort_level": self.calculate_thermal_comfort(current_weather),
            "hvac_load": self.calculate_cooling_load_factor(current_weather),
            "natural_lighting": self.assess_natural_lighting(current_weather),
            "priority_actions": []
        }
        
        if temp is not None and temp > 30:
            insights["priority_actions"].append("High temperature - optimize cooling systems")
        
        if humidity is not None and humidity > 75:
            insights["priority_actions"].append("High humidity - increase dehumidification")
        
        if "rain" in condition.lower():
            insights["priority_actions"].append("Rainy conditions - check building envelope")
        
        return insights

    def calculate_energy_efficiency_score(self, current_weather: Dict[str, Any]) -> float:
        """Calculate energy efficiency score (0-1 scale)"""
        temp = current_weather.get("temperature", 25)
        humidity = current_weather.get("humidity", 50)
        condition = current_weather.get("condition", "").lower()
        
        # Base score from temperature (optimal around 22-26°C)
        if 22 <= temp <= 26:
            temp_score = 1.0
        else:
            temp_score = max(0, 1.0 - abs(temp - 24) / 15)
        
        # Humidity score (optimal around 40-60%)
        if 40 <= humidity <= 60:
            humidity_score = 1.0
        else:
            humidity_score = max(0, 1.0 - abs(humidity - 50) / 40)
        
        # Natural lighting bonus
        lighting_bonus = 0.2 if "clear" in condition or "sunny" in condition else 0
        
        return min(1.0, (temp_score + humidity_score) / 2 + lighting_bonus)

# FastAPI HTTP Server wrapper
app = FastAPI(title="Weather MCP Server", version="1.0.0")

# Global weather server instance
weather_server_instance = None

@app.on_event("startup")
async def startup_event():
    """Initialize the weather server on startup"""
    global weather_server_instance
    weather_server_instance = WeatherMCPServer()
    await weather_server_instance.__aenter__()
    weather_server_instance.setup_handlers()
    # Add HTTP handlers
    setup_http_handlers(weather_server_instance)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global weather_server_instance
    if weather_server_instance:
        await weather_server_instance.__aexit__(None, None, None)

@app.post("/call_tool")
async def call_tool_endpoint(request: ToolCallRequest):
    """HTTP endpoint to call MCP tools"""
    try:
        global weather_server_instance
        if not weather_server_instance:
            raise HTTPException(status_code=500, detail="Server not initialized")
        
        # Get the tool handler
        tool_handlers = {
            "get_current_weather": weather_server_instance.handle_get_current_weather,
            "get_weather_by_coordinates": weather_server_instance.handle_get_weather_by_coordinates,
            "get_building_weather_analysis": weather_server_instance.handle_get_building_weather_analysis,
            "compare_weather_locations": weather_server_instance.handle_compare_weather_locations
        }
        
        if request.name not in tool_handlers:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {request.name}")
        
        # Call the tool handler
        result = await tool_handlers[request.name](request.arguments)
        
        # Convert MCP result to HTTP response
        response_data = {
            "content": [
                {
                    "type": content.type,
                    "text": content.text
                }
                for content in result.content
            ]
        }
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"Error in tool call: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools")
async def list_tools_endpoint():
    """HTTP endpoint to list available tools"""
    try:
        global weather_server_instance
        if not weather_server_instance:
            raise HTTPException(status_code=500, detail="Server not initialized")
        
        # Get tools list
        tools_result = await weather_server_instance.handle_list_tools()
        
        tools_data = [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            }
            for tool in tools_result.tools
        ]
        
        return JSONResponse(content={"tools": tools_data})
        
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Add individual tool handler methods to the WeatherMCPServer class
def add_tool_handlers(server_instance):
    """Add individual tool handlers for HTTP access"""
    
    async def handle_get_current_weather(arguments: Dict[str, Any]) -> CallToolResult:
        """Handle get_current_weather tool"""
        location = arguments.get("location", "").strip()
        include_forecast = arguments.get("include_forecast", False)
        
        # Handle special case for university
        if location.lower() in ["university", "đại học quốc tế miền đông", "current location"]:
            weather_data = await server_instance.get_university_weather()
        else:
            # Get coordinates for the location
            coords = await server_instance.get_location_coordinates(location)
            if coords:
                weather_data = await server_instance.get_weather_data(
                    coords["latitude"],
                    coords["longitude"],
                    coords["name"]
                )
            else:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Could not find location: {location}"
                        )
                    ]
                )
        
        if include_forecast:
            result = json.dumps(weather_data, indent=2, ensure_ascii=False)
        else:
            result = json.dumps(weather_data.get("current", {}), indent=2, ensure_ascii=False)
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result
                )
            ]
        )
    
    async def handle_get_weather_by_coordinates(arguments: Dict[str, Any]) -> CallToolResult:
        """Handle get_weather_by_coordinates tool"""
        latitude = arguments.get("latitude")
        longitude = arguments.get("longitude")
        location_name = arguments.get("location_name", "Unknown Location")
        
        weather_data = await server_instance.get_weather_data(latitude, longitude, location_name)
        result = json.dumps(weather_data, indent=2, ensure_ascii=False)
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result
                )
            ]
        )
    
    async def handle_get_building_weather_analysis(arguments: Dict[str, Any]) -> CallToolResult:
        """Handle get_building_weather_analysis tool"""
        analysis_type = arguments.get("analysis_type", "comprehensive")
        include_recommendations = arguments.get("include_recommendations", True)
        
        weather_data = await server_instance.get_university_weather()
        current = weather_data.get("current", {})
        
        if analysis_type == "hvac":
            analysis_data = {
                "type": "hvac_analysis",
                "location": server_instance.university_coords["name"],
                "outdoor_conditions": current,
                "hvac_recommendations": server_instance.get_hvac_recommendations(current) if include_recommendations else [],
                "optimal_setpoints": server_instance.calculate_optimal_setpoints(current),
                "timestamp": datetime.now().isoformat()
            }
        elif analysis_type == "energy":
            analysis_data = {
                "type": "energy_analysis",
                "location": server_instance.university_coords["name"],
                "weather_conditions": current,
                "energy_recommendations": server_instance.get_energy_recommendations(current) if include_recommendations else [],
                "cooling_load_factor": server_instance.calculate_cooling_load_factor(current),
                "natural_lighting_potential": server_instance.assess_natural_lighting(current),
                "timestamp": datetime.now().isoformat()
            }
        elif analysis_type == "comfort":
            analysis_data = {
                "type": "comfort_analysis",
                "location": server_instance.university_coords["name"],
                "weather_conditions": current,
                "comfort_recommendations": server_instance.get_comfort_recommendations(current) if include_recommendations else [],
                "thermal_comfort_index": server_instance.calculate_thermal_comfort(current),
                "timestamp": datetime.now().isoformat()
            }
        else:  # comprehensive
            analysis_data = {
                "type": "comprehensive_analysis",
                "location": server_instance.university_coords["name"],
                "current_conditions": current,
                "forecast": weather_data.get("daily_forecast", [])[:3],
                "hvac_recommendations": server_instance.get_hvac_recommendations(current) if include_recommendations else [],
                "energy_recommendations": server_instance.get_energy_recommendations(current) if include_recommendations else [],
                "comfort_recommendations": server_instance.get_comfort_recommendations(current) if include_recommendations else [],
                "building_insights": server_instance.get_building_insights(current),
                "timestamp": datetime.now().isoformat()
            }
        
        result = json.dumps(analysis_data, indent=2, ensure_ascii=False)
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result
                )
            ]
        )
    
    async def handle_compare_weather_locations(arguments: Dict[str, Any]) -> CallToolResult:
        """Handle compare_weather_locations tool"""
        locations = arguments.get("locations", [])
        metrics = arguments.get("metrics", ["temperature", "humidity", "condition"])
        
        if len(locations) < 2:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Please provide at least 2 locations to compare"
                    )
                ]
            )
        
        comparison_data = {
            "type": "weather_comparison",
            "locations": [],
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
        for location in locations[:5]:  # Limit to 5 locations
            try:
                if location.lower() == "university":
                    weather_data = await server_instance.get_university_weather()
                else:
                    coords = await server_instance.get_location_coordinates(location)
                    if coords:
                        weather_data = await server_instance.get_weather_data(
                            coords["latitude"],
                            coords["longitude"],
                            coords["name"]
                        )
                    else:
                        continue
                
                comparison_data["locations"].append({
                    "name": location,
                    "weather": weather_data.get("current", {})
                })
                
            except Exception as e:
                logger.error(f"Error getting weather for {location}: {e}")
                continue
        
        result = json.dumps(comparison_data, indent=2, ensure_ascii=False)
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result
                )
            ]
        )
    
    # Add methods to the server instance
    server_instance.handle_get_current_weather = handle_get_current_weather
    server_instance.handle_get_weather_by_coordinates = handle_get_weather_by_coordinates  
    server_instance.handle_get_building_weather_analysis = handle_get_building_weather_analysis
    server_instance.handle_compare_weather_locations = handle_compare_weather_locations
    
    return server_instance

# Modify the WeatherMCPServer class to add the handlers
def setup_http_handlers(server_instance):
    """Setup HTTP handlers for the weather server"""
    return add_tool_handlers(server_instance)

async def run_http_server():
    """Run the HTTP server"""
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()
        
async def main():
    """Main function to run the MCP server"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        # Run HTTP server
        print("Starting Weather MCP HTTP Server on port 8000...")
        await run_http_server()
    else:
        # Run traditional MCP server with stdio
        async with WeatherMCPServer() as weather_server:
            weather_server.setup_handlers()
            
            # Run the server with stdio transport
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await weather_server.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="weather-mcp-server",
                        server_version="1.0.0",
                        capabilities=weather_server.capabilities
                    )
                )

if __name__ == "__main__":
    asyncio.run(main())

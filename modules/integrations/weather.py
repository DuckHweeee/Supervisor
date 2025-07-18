"""
Weather Integration Module for Smart Building AI

This module provides weather data integration and building optimization
recommendations that can be used by any system.
"""

import asyncio
import json
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime


class WeatherIntegration:
    """
    Weather data integration with building optimization recommendations
    """
    
    def __init__(self, 
                 server_url: str = "http://localhost:8001",
                 fallback_data: Optional[Dict[str, Any]] = None):
        """
        Initialize weather integration
        
        Args:
            server_url: URL of the weather API server
            fallback_data: Fallback weather data when API is unavailable
        """
        self.server_url = server_url
        self.client = None
        
        # Default fallback data
        self.fallback_data = fallback_data or {
            "temperature": 26.0,
            "humidity": 80,
            "condition": "Partly Cloudy",
            "coordinates": "11.052754371982356, 106.666777616965",
            "message": "Using cached weather data (API server unavailable)"
        }
    
    async def get_weather_data(self, 
                             location: str, 
                             include_forecast: bool = False) -> Dict[str, Any]:
        """
        Get weather data from the API server
        
        Args:
            location: Location name or coordinates
            include_forecast: Whether to include forecast data
            
        Returns:
            Weather data dictionary
        """
        try:
            # Create httpx client if not exists
            if self.client is None:
                self.client = httpx.AsyncClient(timeout=30.0)
            
            # Call the weather API
            payload = {
                "location": location,
                "units": "metric",
                "include_forecast": include_forecast
            }
            
            response = await self.client.post(f"{self.server_url}/weather", json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                return self._get_fallback_weather(location)
                
        except Exception as e:
            print(f"Error connecting to weather API server: {e}")
            return self._get_fallback_weather(location)
    
    def _get_fallback_weather(self, location: str) -> Dict[str, Any]:
        """Get fallback weather data when API server is unavailable"""
        return {
            "location": location,
            **self.fallback_data
        }
    
    def get_weather_sync(self, location: str, include_forecast: bool = False) -> Dict[str, Any]:
        """
        Synchronous version of get_weather_data for non-async environments
        
        Args:
            location: Location name or coordinates
            include_forecast: Whether to include forecast data
            
        Returns:
            Weather data dictionary
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, use fallback
                return self._get_fallback_weather(location)
        except RuntimeError:
            # No event loop exists, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(
                self.get_weather_data(location, include_forecast)
            )
        except Exception as e:
            print(f"Error getting weather data: {e}")
            return self._get_fallback_weather(location)
    
    def format_weather_response(self, 
                              weather_data: Dict[str, Any], 
                              include_building_recommendations: bool = True) -> str:
        """
        Format weather data into a readable response with building recommendations
        
        Args:
            weather_data: Raw weather data
            include_building_recommendations: Whether to include building optimization tips
            
        Returns:
            Formatted weather response string
        """
        response_parts = []
        
        # Current weather information
        if weather_data.get('temperature') and weather_data.get('temperature') != 'unknown':
            location = weather_data.get('location', 'Unknown Location')
            response_parts.append(f"📍 **Current Weather at {location}:**")
            
            # Temperature
            temp = weather_data.get('temperature', 'N/A')
            if isinstance(temp, (int, float)):
                response_parts.append(f"🌡️ Temperature: {temp}°C")
            else:
                response_parts.append(f"🌡️ Temperature: {temp}")
            
            # Additional weather details
            if weather_data.get('feels_like'):
                response_parts.append(f"🌡️ Feels like: {weather_data['feels_like']}")
            
            if weather_data.get('humidity'):
                response_parts.append(f"💧 Humidity: {weather_data['humidity']}%")
            
            if weather_data.get('condition'):
                response_parts.append(f"🌤️ Condition: {weather_data['condition']}")
            
            if weather_data.get('wind_speed'):
                response_parts.append(f"💨 Wind: {weather_data['wind_speed']} km/h")
            
            if weather_data.get('pressure'):
                response_parts.append(f"📊 Pressure: {weather_data['pressure']} hPa")
        
        # Forecast if available
        if weather_data.get('forecast'):
            response_parts.append(f"\n📅 **3-Day Forecast:**")
            for day in weather_data['forecast'][:3]:
                date = day.get('date', 'Unknown date')
                max_temp = day.get('max_temp', 'N/A')
                min_temp = day.get('min_temp', 'N/A')
                condition = day.get('condition', 'Unknown')
                response_parts.append(f"  {date}: {max_temp}°/{min_temp}° - {condition}")
        
        # Building recommendations
        if include_building_recommendations:
            recommendations = self.get_building_recommendations(weather_data)
            if recommendations:
                response_parts.append(f"\n🏢 **Smart Building Recommendations:**")
                response_parts.extend(recommendations)
        
        # Add message if available
        if weather_data.get('message'):
            response_parts.append(f"\n⚠️ **Note:** {weather_data['message']}")
        
        return "\n".join(response_parts)
    
    def get_building_recommendations(self, weather_data: Dict[str, Any]) -> List[str]:
        """
        Generate building optimization recommendations based on weather data
        
        Args:
            weather_data: Weather data dictionary
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        try:
            # Extract temperature
            temp = weather_data.get('temperature')
            if isinstance(temp, str):
                temp = float(temp.replace('°C', '').replace('°F', ''))
            elif not isinstance(temp, (int, float)):
                return recommendations
            
            # Extract humidity
            humidity = weather_data.get('humidity', 0)
            if isinstance(humidity, str):
                humidity = float(humidity.replace('%', ''))
            
            # Extract condition
            condition = weather_data.get('condition', '').lower()
            
            # Temperature-based recommendations
            if temp < 18:  # Cold weather
                recommendations.append("❄️ **Cold Weather:** Increase HVAC heating to 20-22°C. Check window seals and increase insulation efficiency.")
                recommendations.append("💡 **Lighting:** Increase indoor lighting as daylight may be limited. Consider warm light settings for comfort.")
            elif temp > 28:  # Hot weather
                recommendations.append("🔥 **Hot Weather:** Optimize cooling to 22-24°C. Use smart blinds to reduce solar heat gain.")
                recommendations.append("⚡ **Energy:** Monitor peak cooling loads. Consider load balancing during high-demand periods.")
            else:  # Moderate temperature
                recommendations.append("🌡️ **Optimal Conditions:** Maintain HVAC at 20-22°C for energy efficiency. Good weather for natural ventilation.")
            
            # Humidity-based recommendations
            if humidity > 70:
                recommendations.append("💧 **High Humidity:** Increase dehumidification. Monitor for condensation and mold risk. Ensure proper ventilation.")
            elif humidity < 30:
                recommendations.append("🏜️ **Low Humidity:** Consider humidification for comfort. Monitor static electricity and dust levels.")
            
            # Condition-based recommendations
            if any(term in condition for term in ['rain', 'storm', 'thunderstorm']):
                recommendations.append("🌧️ **Rainy Weather:** Close windows and rely on HVAC. Check drainage systems and water intrusion points.")
            elif any(term in condition for term in ['sunny', 'clear']):
                recommendations.append("☀️ **Sunny Weather:** Utilize natural lighting. Deploy solar shading to prevent overheating.")
            elif any(term in condition for term in ['cloudy', 'overcast']):
                recommendations.append("☁️ **Cloudy Weather:** Optimize artificial lighting. Good conditions for natural ventilation.")
            elif any(term in condition for term in ['wind']):
                recommendations.append("💨 **Windy Conditions:** Secure outdoor equipment. Consider natural ventilation opportunities.")
            
            # Energy optimization
            if temp > 25 or temp < 20:
                recommendations.append("🔋 **Energy Tip:** Weather conditions require active HVAC. Monitor energy consumption and optimize schedules.")
            else:
                recommendations.append("🌿 **Energy Savings:** Mild weather allows for reduced HVAC usage. Consider natural ventilation and lighting.")
            
        except (ValueError, TypeError) as e:
            print(f"Error generating recommendations: {e}")
            recommendations.append("⚠️ **Weather Data:** Unable to process weather data for specific recommendations.")
        
        return recommendations
    
    async def close(self):
        """Close the HTTP client"""
        if self.client:
            await self.client.aclose()
    
    def get_integration_info(self) -> Dict[str, Any]:
        """Get information about the weather integration"""
        return {
            "server_url": self.server_url,
            "fallback_available": bool(self.fallback_data),
            "client_active": self.client is not None,
            "features": [
                "Real-time weather data",
                "Weather forecasts",
                "Building optimization recommendations",
                "Fallback data support",
                "Async and sync interfaces"
            ]
        }


# Factory function
def create_weather_integration(server_url: str = "http://localhost:8001",
                             fallback_data: Optional[Dict[str, Any]] = None) -> WeatherIntegration:
    """
    Factory function to create a weather integration instance
    
    Args:
        server_url: URL of the weather API server
        fallback_data: Fallback weather data
        
    Returns:
        WeatherIntegration instance
    """
    return WeatherIntegration(server_url, fallback_data)


# Tool function for AI integration
def create_weather_tool(weather_integration: WeatherIntegration):
    """
    Create a weather tool function that can be registered with the AI agent
    
    Args:
        weather_integration: WeatherIntegration instance
        
    Returns:
        Tool function
    """
    def weather_tool(location: str, 
                    include_forecast: bool = False,
                    include_recommendations: bool = True) -> str:
        """
        Get weather information and building recommendations
        
        Args:
            location: Location name or coordinates
            include_forecast: Include weather forecast
            include_recommendations: Include building optimization recommendations
            
        Returns:
            Formatted weather response
        """
        try:
            # Get weather data
            weather_data = weather_integration.get_weather_sync(location, include_forecast)
            
            # Format response
            response = weather_integration.format_weather_response(
                weather_data, include_recommendations
            )
            
            return response
            
        except Exception as e:
            return f"Error getting weather information: {str(e)}"
    
    return weather_tool


# Example usage
if __name__ == "__main__":
    # Create weather integration
    weather = create_weather_integration()
    
    # Test sync weather
    weather_data = weather.get_weather_sync("Ho Chi Minh City")
    print("Weather Data:", json.dumps(weather_data, indent=2))
    
    # Test formatted response
    response = weather.format_weather_response(weather_data)
    print("\nFormatted Response:")
    print(response)
    
    # Get integration info
    info = weather.get_integration_info()
    print("\nIntegration Info:", json.dumps(info, indent=2))

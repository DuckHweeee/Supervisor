# Smart Building AI Assistant - Weather Integration

## Overview

The Smart Building AI Assistant now uses **real-time weather data** from the Open-Meteo API instead of static weather data. This provides accurate, up-to-date weather information for building management and HVAC optimization.

## Architecture

### Components

1. **Weather API Server** (`weather_api_server.py`)
   - FastAPI-based HTTP server
   - Integrates with Open-Meteo weather API
   - Provides REST endpoints for weather data
   - Runs on port 8001

2. **Weather API Client** (in `AutoGenAI.py`)
   - HTTP client that connects to the weather API server
   - Handles fallback to cached data when server is unavailable
   - Integrated with AutoGen agents

3. **Streamlit Chat Interface** (`streamlit_app.py`)
   - Interactive chat UI
   - Uses the weather-enabled AI assistant
   - Real-time weather queries through chat

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `fastapi` - Web framework for the weather API
- `uvicorn` - ASGI server for FastAPI
- `httpx` - HTTP client for API calls
- `pydantic` - Data validation

### 2. Start the Weather API Server

```bash
python weather_api_server.py
```

Or use the helper script:
```bash
python start_weather_server.py
```

The server will start on `http://localhost:8001`

### 3. Start the Streamlit Chat Interface

```bash
streamlit run streamlit_app.py
```

The chat interface will be available at `http://localhost:8502`

## Usage

### Chat Interface Queries

You can now ask weather-related questions in the chat interface:

**Current Weather:**
- "What's the weather like at the university?"
- "What's the current temperature?"
- "How's the weather outside?"

**Specific Locations:**
- "What's the weather in Ho Chi Minh City?"
- "Show me the weather in Saigon"

**Weather Forecasts:**
- "What's the weather forecast for the university?"
- "Give me the 3-day forecast"

### API Endpoints

The weather API server provides these endpoints:

#### GET `/health`
Health check endpoint
```json
{
  "status": "healthy",
  "timestamp": "2025-07-03T13:00:00",
  "service": "Weather API Server"
}
```

#### GET `/weather/university`
Get current weather for the university location
```json
{
  "current": {
    "location": "Đại học quốc tế Miền Đông",
    "temperature": 31.8,
    "humidity": 63,
    "condition": "Overcast",
    "coordinates": "11.052754371982356, 106.666777616965",
    "feels_like": 36.5,
    "wind_speed": 9.7,
    "pressure": 1003.8,
    "timestamp": "2025-07-03T13:00"
  }
}
```

#### POST `/weather`
Get weather for any location
```json
{
  "location": "Ho Chi Minh City",
  "units": "metric",
  "include_forecast": true
}
```

## Weather Data Features

### Current Weather
- **Temperature**: Real-time temperature in Celsius
- **Humidity**: Relative humidity percentage
- **Condition**: Weather condition (e.g., "Overcast", "Partly Cloudy")
- **Feels Like**: Apparent temperature
- **Wind Speed**: Wind speed in km/h
- **Pressure**: Atmospheric pressure in hPa
- **Timestamp**: When the data was collected

### 3-Day Forecast
- **Daily High/Low**: Maximum and minimum temperatures
- **Weather Conditions**: Daily weather conditions
- **Precipitation**: Expected rainfall in mm

### Smart Building Integration
The weather data is specifically useful for:
- **HVAC Optimization**: Adjust heating/cooling based on outdoor conditions
- **Energy Management**: Optimize energy usage based on weather patterns
- **Comfort Control**: Maintain optimal indoor conditions
- **Predictive Maintenance**: Plan maintenance based on weather forecasts

## Fallback Mechanism

The system includes a robust fallback mechanism:

1. **Primary**: Live weather data from Open-Meteo API
2. **Fallback**: Cached weather data when API is unavailable
3. **Error Handling**: Graceful degradation with informative messages

## Testing

### Test Scripts

1. **Test Weather API Server**:
   ```bash
   python test_weather_api.py
   ```

2. **Test AutoGen Integration**:
   ```bash
   python AutoGenAI.py
   ```

### Manual Testing

1. Start the weather API server
2. Open the Streamlit chat interface
3. Ask weather questions like:
   - "What's the weather like?"
   - "How hot is it outside?"
   - "What's the forecast for tomorrow?"

## Configuration

### University Location
The system is pre-configured for:
- **Location**: Đại học quốc tế Miền Đông
- **Coordinates**: 11.052754371982356, 106.666777616965
- **Timezone**: Asia/Ho_Chi_Minh

### API Settings
- **Weather API**: Open-Meteo (free, no API key required)
- **Server Port**: 8001
- **Timeout**: 30 seconds
- **Fallback**: Cached data

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Change the port in `weather_api_server.py`
   - Update the port in `AutoGenAI.py` client configuration

2. **API Server Not Starting**
   - Check if required packages are installed
   - Verify no other service is using the port

3. **Weather Data Not Updating**
   - Ensure the weather API server is running
   - Check internet connectivity
   - Verify Open-Meteo API is accessible

4. **Fallback Data Being Used**
   - Check if the weather API server is running on the correct port
   - Verify the client is connecting to the right URL

### Logs and Debugging

- Weather API server logs are displayed in the terminal
- Client connection errors are logged in the console
- Check the Streamlit interface for error messages

## Future Enhancements

Potential improvements to the weather system:

1. **Weather Alerts**: Integration with weather warning systems
2. **Historical Data**: Access to historical weather patterns
3. **Multiple Locations**: Support for multiple building locations
4. **Weather-Based Automation**: Automatic HVAC adjustments
5. **Energy Predictions**: Weather-based energy consumption forecasts

## Files Overview

- `weather_api_server.py` - Main weather API server
- `AutoGenAI.py` - Contains weather client and integration
- `streamlit_app.py` - Chat interface (uses weather-enabled assistant)
- `start_weather_server.py` - Helper script to start weather server
- `test_weather_api.py` - Test script for weather functionality
- `requirements.txt` - Python dependencies

## Support

For issues or questions about the weather integration:
1. Check the terminal output for error messages
2. Verify all dependencies are installed
3. Ensure the weather API server is running
4. Test with the provided test scripts

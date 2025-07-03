# Smart Building AI Assistant

A comprehensive AI-powered assistant for smart building management using AutoGen, real-time weather data, and a knowledge base system.

## 🏢 Features

### Core Capabilities
- **Interactive Chat Interface**: Modern Streamlit-based chat UI
- **Real-time Weather Integration**: Live weather data from Open-Meteo API
- **Knowledge Base**: Document search and retrieval using ChromaDB
- **Smart Building Expertise**: HVAC, lighting, security, and energy management
- **Document Processing**: Support for PDF, DOCX, Excel, JSON, and text files

### Weather Integration
- **Real-time Data**: Current weather conditions and 3-day forecasts
- **Smart Building Optimization**: Weather-based HVAC and energy recommendations
- **Multiple Locations**: Support for university location and custom locations
- **Fallback System**: Cached data when API is unavailable

### Knowledge Base
- **Document Ingestion**: Automatic processing of building manuals and specifications
- **Semantic Search**: Find relevant information across all documents
- **Multiple Formats**: PDF, DOCX, Excel, CSV, JSON, and text files
- **Auto-loading**: Automatically loads documents from the `smart_building_data` folder

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd smart-building-ai

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Weather API Server

```bash
python weather_api_server.py
```

The weather server will start on `http://localhost:8001`

### 3. Start the Chat Interface

```bash
streamlit run streamlit_app.py
```

The chat interface will be available at `http://localhost:8502`

### 4. Start Chatting!

Ask questions like:
- "What's the weather like at the university?"
- "How do I maintain the HVAC system?"
- "What are the lighting specifications?"
- "Show me the building energy usage data"

## 📁 Project Structure

```
smart-building-ai/
├── AutoGenAI.py                 # Main AI assistant with weather integration
├── streamlit_app.py             # Chat interface
├── weather_api_server.py        # Weather API server
├── start_weather_server.py      # Helper script for weather server
├── test_weather_api.py          # Weather system tests
├── requirements.txt             # Python dependencies
├── WEATHER_INTEGRATION.md       # Weather system documentation
├── smart_building_data/         # Knowledge base documents
│   ├── building_data.json       # Building data and specifications
│   ├── hvac_manual.txt          # HVAC maintenance manual
│   └── lighting_specifications.txt # Lighting system specs
└── knowledge_base/              # ChromaDB vector database
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file with your Groq API key:
```
GROQ_API_KEY=your_groq_api_key_here
```

### University Location
Pre-configured for:
- **Name**: Đại học quốc tế Miền Đông
- **Coordinates**: 11.052754371982356, 106.666777616965
- **Timezone**: Asia/Ho_Chi_Minh

## 🌤️ Weather System

### Real-time Weather Data
- **Current Conditions**: Temperature, humidity, pressure, wind
- **Weather Forecasts**: 3-day forecast with daily high/low
- **Smart Building Integration**: Weather-based HVAC optimization
- **Multiple Locations**: University and custom locations

### API Endpoints
- `GET /health` - Health check
- `GET /weather/university` - University weather
- `POST /weather` - Weather by location

### Example Weather Response
```json
{
  "location": "Đại học quốc tế Miền Đông",
  "temperature": "31.8°C",
  "humidity": "63%",
  "condition": "Overcast",
  "feels_like": "36.5°C",
  "wind_speed": "9.7 km/h",
  "pressure": "1003.8 hPa",
  "timestamp": "2025-07-03T13:00"
}
```

## 📚 Knowledge Base

### Document Types Supported
- **PDF**: Manuals, specifications, reports
- **DOCX**: Maintenance guides, procedures
- **Excel/CSV**: Building data, sensor readings
- **JSON**: Structured building information
- **Text**: General documentation

### Adding Documents
1. Place documents in the `smart_building_data/` folder
2. The system will automatically process them on startup
3. Use the chat interface to search through documents

### Example Queries
- "What's the HVAC maintenance schedule?"
- "Show me the lighting specifications"
- "What are the building automation systems?"

## 🤖 AI Assistant Capabilities

### Smart Building Expertise
- **HVAC Systems**: Maintenance, optimization, troubleshooting
- **Lighting Control**: LED systems, energy efficiency
- **Security Systems**: Access control, surveillance
- **Energy Management**: Consumption monitoring, optimization
- **IoT Integration**: Sensor data, automation

### Weather-Based Recommendations
- **HVAC Optimization**: Temperature and humidity control
- **Energy Efficiency**: Weather-based energy saving
- **Comfort Management**: Indoor climate optimization
- **Predictive Maintenance**: Weather-based scheduling

## 🧪 Testing

### Test the Weather System
```bash
python test_weather_api.py
```

### Test the Main Assistant
```bash
python AutoGenAI.py
```

### Test Questions
Use the provided test questions in `test_questions.py`:
```bash
python test_questions.py
```

## 🛠️ Development

### Adding New Documents
1. Add documents to `smart_building_data/`
2. Restart the system to auto-load them
3. Or use the chat interface: "Add this document to the knowledge base"

### Extending Weather Features
- Modify `weather_api_server.py` for new weather endpoints
- Update `AutoGenAI.py` for new weather tools
- Add weather-based automation in the assistant

### Custom Locations
- Add coordinates to the weather service
- Update location handling in the API server
- Configure timezone settings

## 📊 Usage Examples

### Weather Queries
```
User: "What's the weather like right now?"
Assistant: "The current weather at Đại học quốc tế Miền Đông is 31.8°C with overcast conditions. The humidity is 63% and it feels like 36.5°C. Wind speed is 9.7 km/h."

User: "Should we adjust the HVAC system?"
Assistant: "Based on the current weather (31.8°C, 63% humidity), I recommend setting the cooling system to 22°C with increased ventilation due to the high temperature and humidity levels."
```

### Knowledge Base Queries
```
User: "How do I maintain the HVAC system?"
Assistant: "According to the HVAC manual, regular maintenance includes: 1) Monthly filter replacement, 2) Quarterly coil cleaning, 3) Annual system inspection..."

User: "What are the lighting specifications?"
Assistant: "The building uses LED-based smart lighting with IoT integration. The system includes motion sensors, daylight harvesting, and centralized control..."
```

## 🔍 Troubleshooting

### Common Issues

1. **Weather API Not Working**
   - Check if `weather_api_server.py` is running
   - Verify internet connectivity
   - Check port 8001 is available

2. **Knowledge Base Empty**
   - Ensure documents are in `smart_building_data/`
   - Check file permissions
   - Verify supported file formats

3. **Chat Interface Not Loading**
   - Check if Streamlit is installed
   - Verify port 8502 is available
   - Check for error messages in terminal

### Debug Commands
```bash
# Check weather server status
curl http://localhost:8001/health

# Test weather API
curl -X POST http://localhost:8001/weather -H "Content-Type: application/json" -d '{"location": "university"}'

# Check knowledge base
python -c "from AutoGenAI import get_knowledge_base_stats; print(get_knowledge_base_stats())"
```

## 📈 Performance

- **Weather API**: ~1-2 second response time
- **Knowledge Base**: ~0.5-1 second search time
- **Chat Interface**: Real-time responses
- **Document Processing**: ~1-5 seconds per document

## 🔒 Security

- **No API Keys Required**: Uses free Open-Meteo API
- **Local Processing**: All documents processed locally
- **No External Dependencies**: Knowledge base stored locally
- **Secure Communication**: HTTP/HTTPS supported

## 🚀 Future Enhancements

- **Weather Alerts**: Integration with weather warning systems
- **Historical Data**: Weather pattern analysis
- **Mobile App**: Native mobile interface
- **Voice Control**: Voice commands for building control
- **IoT Integration**: Real sensor data integration
- **Energy Optimization**: AI-powered energy management

## 📞 Support

For issues or questions:
1. Check the terminal output for error messages
2. Review the documentation files
3. Test with the provided test scripts
4. Ensure all dependencies are installed

## 📄 License

This project is for educational and demonstration purposes. Weather data provided by Open-Meteo API.

---

**Happy Building Management! 🏢✨**

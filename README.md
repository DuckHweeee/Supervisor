# Smart Building AI Assistant

A comprehensive AI-powered assistant for smart building management using AutoGen, real-time weather data, and a knowledge base system.

## 🏢 System Overview

This optimized system provides intelligent building management through:
- **Streamlit Web Interface** (`streamlit_app.py`) - Main user interface
- **AutoGen AI Core** (`AutoGenAI.py`) - AI agent functionality
- **Weather API Server** (`weather_api_server.py`) - Real-time weather data
- **ChromaDB Integration** (`chromadb_compat.py`) - Knowledge base system

## 🚀 Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
Create `.env` file with:
```
GROQ_API_KEY=your_groq_api_key
OPENWEATHER_API_KEY=your_openweather_key  # Optional
```

### 3. Run Application
```bash
# Start the Streamlit app
streamlit run streamlit_app.py

# Or use the batch file
run_streamlit.bat
```

### 4. Optional: Start Weather Server
```bash
python weather_api_server.py
# Or use: python start_weather_server.py
```

## 📁 Core Files Structure

```
📦 Smart Building AI System
├── 🎯 **Main Applications**
│   ├── streamlit_app.py          # Primary Streamlit interface (89KB)
│   ├── AutoGenAI.py              # Core AutoGen AI functionality (76KB)
│   └── weather_api_server.py     # Weather API server (11KB)
│
├── 🔧 **Core Support**
│   ├── chromadb_compat.py        # ChromaDB compatibility wrapper
│   ├── start_app.py              # Application starter
│   └── start_weather_server.py   # Weather server starter
│
├── 📋 **Configuration**
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Environment variables
│   └── .gitignore               # Git ignore rules
│
├── 🏃 **Launch Scripts**
│   ├── run_streamlit.bat         # Windows batch launcher
│   ├── run_streamlit.ps1         # PowerShell launcher
│   └── start_app.bat            # Application launcher
│
├── 📊 **Data Directories**
│   ├── knowledge_base/           # ChromaDB vector store
│   ├── smart_building_data/      # Building documents & data
│   └── coding/                   # AutoGen code execution workspace
│
└── 📚 **Documentation**
    ├── README.md                 # This file - main documentation
    ├── SETUP_GUIDE.md           # Detailed setup instructions
    ├── DEPLOYMENT_FIX.md        # Deployment troubleshooting
    ├── SSL_ERROR_HANDLING_GUIDE.md # SSL configuration help
    ├── AUTO_TRAINING_GUIDE.md   # AI training instructions
    ├── TRAINING_QUESTIONS_GUIDE.md # Training data guide
    ├── WEATHER_INTEGRATION.md   # Weather API documentation
    └── WEB_TRAINING_GUIDE.md    # Web content training guide
```

## 🏢 Features

### Core Capabilities
- **Interactive Chat Interface**: Modern Streamlit-based chat UI
- **Real-time Weather Integration**: Live weather data with building optimization
- **Knowledge Base**: Document search and retrieval using ChromaDB
- **Smart Building Expertise**: HVAC, lighting, security, and energy management
- **Document Processing**: Support for PDF, DOCX, Excel, JSON, and text files
- **Web Content Training**: Extract and learn from building management websites

### Weather Integration
- **Real-time Data**: Current weather conditions and 3-day forecasts
- **Smart Building Optimization**: Weather-based HVAC and energy recommendations
- **Multiple Locations**: Support for university location and custom locations
- **Fallback System**: Cached data when API is unavailable

### Knowledge Base
- **Multi-format Support**: PDF, DOCX, TXT, Excel, JSON files
- **Web Content Integration**: Train from building management websites
- **Intelligent Search**: Vector-based document retrieval
- **Context-aware Responses**: Synthesized information with actionable insights

### AutoGen Integration
- **Intelligent Agents**: Assistant and User Proxy agents
- **Tool Integration**: Weather data, knowledge base search, web training
- **Code Execution**: Safe code execution environment
- **Conversation Management**: Multi-turn conversations with context

## 🔧 System Architecture

### Main Components

1. **Streamlit App** (`streamlit_app.py`)
   - Primary user interface
   - Chat functionality
   - File upload and processing
   - Knowledge base management
   - Web training interface

2. **AutoGen AI Core** (`AutoGenAI.py`)
   - AI agent definitions
   - Tool registrations
   - Weather integration
   - Knowledge base integration

3. **Weather API Server** (`weather_api_server.py`)
   - FastAPI-based weather service
   - Real-time weather data
   - Building optimization recommendations
   - Fallback data handling

4. **ChromaDB Compatibility** (`chromadb_compat.py`)
   - Vector database wrapper
   - Cross-platform compatibility
   - Error handling and fallbacks

### Dependencies
- **AutoGen**: AI agent framework
- **Streamlit**: Web interface
- **ChromaDB**: Vector database
- **FastAPI**: Weather API server
- **OpenAI/Groq**: LLM integration
- **Document Processing**: PyPDF2, python-docx, openpyxl, pandas

## 🎯 Usage Examples

### Basic Chat
```
Ask: "What's the optimal HVAC temperature setting?"
Response: Detailed recommendations with energy efficiency tips
```

### Weather Integration
```
Ask: "Check weather and optimize building systems"
Response: Current weather + specific building optimization recommendations
```

### Knowledge Base
```
Ask: "Upload HVAC manual and ask maintenance questions"
Response: Document-based answers with specific procedures
```

### Web Training
```
Ask: "Train from building management websites"
Response: Extracts and integrates industry best practices
```

## 🛠 Troubleshooting

### Common Issues

1. **AutoGen Import Error**
   - Install: `pip install pyautogen autogen`
   - See: `DEPLOYMENT_FIX.md`

2. **ChromaDB Issues**
   - Uses compatibility wrapper with fallbacks
   - See: `chromadb_compat.py`

3. **SSL Certificate Errors**
   - See: `SSL_ERROR_HANDLING_GUIDE.md`
   - Automatic fallback handling included

4. **Weather API Issues**
   - Fallback data system activated automatically
   - Check API key configuration

### Performance Optimization

- **Memory**: ChromaDB uses efficient vector storage
- **Response Time**: Local embeddings for fast search
- **Scalability**: Modular architecture supports growth
- **Error Handling**: Comprehensive fallback systems

## 📈 System Performance

### File Size Optimization
- **Before**: 45+ files, multiple duplicates
- **After**: ~15 core files, optimized structure
- **Reduction**: ~67% file count reduction
- **Maintained**: All core functionality

### Key Optimizations
- ✅ Removed 30+ duplicate/test files
- ✅ Consolidated documentation
- ✅ Streamlined requirements
- ✅ Cleaned cache directories
- ✅ Removed obsolete training files

## 🔐 Security & Privacy

- **API Keys**: Secure environment variable storage
- **Data Privacy**: Local document processing
- **SSL Handling**: Automatic certificate validation
- **Error Logging**: Secure error reporting

## 🚀 Deployment

### Local Development
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Cloud Deployment
1. Ensure `requirements.txt` is current
2. Set environment variables
3. Deploy to Streamlit Cloud or similar platform

### Docker Deployment
```dockerfile
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "streamlit_app.py"]
```

## 📞 Support

For detailed setup and troubleshooting:
- **Setup**: See `SETUP_GUIDE.md`
- **Deployment**: See `DEPLOYMENT_FIX.md`
- **Training**: See `AUTO_TRAINING_GUIDE.md`
- **Weather**: See `WEATHER_INTEGRATION.md`

## 📊 System Stats

- **Core Files**: 15 essential files
- **Total Size**: ~200KB core code
- **Dependencies**: 25+ packages
- **Features**: 50+ AI capabilities
- **Optimization**: 67% file reduction

---

**Built with**: AutoGen, Streamlit, ChromaDB, FastAPI, and modern AI technologies for intelligent building management.

# Smart Building AI Assistant - Setup Guide

## ✅ Quick Start (Fixed Dependencies)

The dependency issues have been resolved! Here's how to get started:

### 1. Dependencies Status
- ✅ All required packages are now correctly specified
- ✅ Removed invalid `model-context-protocol` package
- ✅ Added proper version constraints
- ✅ Fixed import issues

### 2. Environment Setup

1. **Install Dependencies** (if not already done):
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Environment Variables**:
   Create a `.env` file in the project directory:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

3. **Verify Installation**:
   ```bash
   python test_dependencies.py
   ```

### 3. Running the Application

**Option 1: Using the launcher script**
```bash
python start_app.py
```

**Option 2: Using batch file (Windows)**
```bash
start_app.bat
```

**Option 3: Direct streamlit command**
```bash
streamlit run streamlit_app.py
```

### 4. Features Available

🏢 **Smart Building Management:**
- HVAC system optimization
- Energy management and monitoring
- Lighting control systems
- Security and access control
- Building automation and IoT integration

🌐 **Web Integration:**
- Real-time weather data integration
- Web content training for up-to-date information
- Industry standards and best practices

🤖 **AI Capabilities:**
- Natural language queries about building systems
- Automated responses with context-aware recommendations
- Document processing and knowledge base management
- Multi-modal training data support

### 5. Testing

Run the included test scripts to verify everything works:

```bash
# Test basic dependencies
python test_dependencies.py

# Test streamlit app components
python test_streamlit_app.py
```

### 6. Troubleshooting

**Common Issues:**
- ❌ `model-context-protocol` not found → **FIXED** (removed invalid package)
- ❌ Missing httpx import → **FIXED** (added proper import)
- ❌ Environment variables not loaded → Create `.env` file with GROQ_API_KEY

**If you encounter issues:**
1. Check Python version (3.8+ recommended)
2. Verify all dependencies are installed: `pip list`
3. Check environment variables are set
4. Run the test scripts to identify specific issues

### 7. File Structure

```
Supervisor/
├── streamlit_app.py           # Main application
├── requirements.txt           # Dependencies (FIXED)
├── start_app.py              # Application launcher
├── start_app.bat             # Windows batch launcher
├── test_dependencies.py      # Dependency test script
├── test_streamlit_app.py     # App component test script
├── .env                      # Environment variables (create this)
└── knowledge_base/           # AI knowledge base storage
```

### 8. Next Steps

1. **Start the app**: `python start_app.py`
2. **Access the web interface**: http://localhost:8501
3. **Upload documents** to train the AI
4. **Ask questions** about building management
5. **Explore web training** features for up-to-date information

The application is now ready to use! 🎉

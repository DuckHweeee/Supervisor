# Deployment Fix Guide

## Issues Fixed

### 1. AutoGen Import Error (RESOLVED)
The original error was:
```
ModuleNotFoundError: This app has encountered an error. The original error message is redacted to prevent data leaks.
File "/mount/src/supervisor/streamlit_app.py", line 7, in <module>
    from autogen import AssistantAgent, UserProxyAgent
```

**Root Cause:** Incorrect package specification in requirements.txt. The file was trying to install `autogen-agentchat` instead of the correct `pyautogen` package.

### 2. ChromaDB SQLite Error (NEW ISSUE)
```
RuntimeError: Your system has an unsupported version of sqlite3. Chroma requires sqlite3 >= 3.35.0.
```

**Root Cause:** Streamlit Cloud (and some other platforms) use older SQLite versions incompatible with ChromaDB.

## Solutions Applied

### 1. AutoGen Package Fix
1. **Fixed the requirements.txt files:**
   - Changed `autogen-agentchat>=0.6.0` to `pyautogen>=0.2.0`
   - Updated both `requirements.txt` and `requirements_fixed.txt`

2. **Verified correct imports:**
   - `from autogen import AssistantAgent, UserProxyAgent` ✅
   - `from autogen.coding import LocalCommandLineCodeExecutor` ✅

### 2. ChromaDB SQLite Compatibility Fix
The app needs to be modified to handle SQLite compatibility issues on deployment platforms.

**Option A: Use pysqlite3-binary (Recommended)**
Add to requirements.txt:
```
pysqlite3-binary>=0.5.0
```

**Option B: Fallback to in-memory storage**
Modify the app to gracefully handle ChromaDB initialization failures.

## Testing
- Created `test_import.py` to verify all imports work correctly
- All dependencies now import successfully
- The Streamlit app should deploy without import errors

## For Future Deployments
1. Use `requirements.txt` or `requirements_fixed.txt` (both are now correct)
2. Ensure `pyautogen>=0.2.0` is specified, not `autogen-agentchat`
3. Test imports locally before deployment using `python test_import.py`

## Key Packages
- `pyautogen>=0.2.0` - The correct AutoGen package
- `streamlit>=1.40.0` - For the web interface
- `chromadb>=1.0.0` - For the knowledge base
- `pysqlite3-binary>=0.5.0` - SQLite compatibility fix for ChromaDB
- `groq>=0.25.0` - For AI model integration
- `requests>=2.31.0` - For web scraping
- `beautifulsoup4>=4.12.0` - For HTML parsing
- `httpx>=0.25.0` - For async HTTP requests

## Final Testing
Run the comprehensive deployment test:
```bash
python test_deployment.py
```

This test verifies:
- ✅ All critical imports work correctly
- ✅ ChromaDB fallback mechanism functions properly  
- ✅ Basic app functionality is operational
- ✅ Both persistent and in-memory storage modes work

## Deployment Commands
```bash
# Install all dependencies
pip install -r requirements.txt

# Test the deployment
python test_deployment.py

# Run the Streamlit app
streamlit run streamlit_app.py
```

## Notes
- The app includes comprehensive smart building management features
- Weather integration is available through local API server
- Knowledge base supports web training from building management websites
- All AutoGen functionality is preserved with correct package
- **ChromaDB SQLite Compatibility**: The app now includes fallback storage for deployment platforms with older SQLite versions
- **Graceful Degradation**: If ChromaDB fails to initialize, the app will use in-memory storage and continue to function
- **Production Ready**: All known deployment issues have been resolved

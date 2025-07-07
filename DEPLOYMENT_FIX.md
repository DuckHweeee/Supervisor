# Deployment Fix Guide

## Issue Fixed
The original error was:
```
ModuleNotFoundError: This app has encountered an error. The original error message is redacted to prevent data leaks.
File "/mount/src/supervisor/streamlit_app.py", line 7, in <module>
    from autogen import AssistantAgent, UserProxyAgent
```

## Root Cause
The issue was caused by incorrect package specification in requirements.txt. The file was trying to install `autogen-agentchat` instead of the correct `pyautogen` package.

## Solution Applied
1. **Fixed the requirements.txt files:**
   - Changed `autogen-agentchat>=0.6.0` to `pyautogen>=0.2.0`
   - Updated both `requirements.txt` and `requirements_fixed.txt`

2. **Verified correct imports:**
   - `from autogen import AssistantAgent, UserProxyAgent` ✅
   - `from autogen.coding import LocalCommandLineCodeExecutor` ✅

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
- `groq>=0.25.0` - For AI model integration
- `requests>=2.31.0` - For web scraping
- `beautifulsoup4>=4.12.0` - For HTML parsing
- `httpx>=0.25.0` - For async HTTP requests

## Deployment Commands
```bash
# Install all dependencies
pip install -r requirements.txt

# Test imports
python test_import.py

# Run the Streamlit app
streamlit run streamlit_app.py
```

## Notes
- The app includes comprehensive smart building management features
- Weather integration is available through local API server
- Knowledge base supports web training from building management websites
- All AutoGen functionality is preserved with correct package

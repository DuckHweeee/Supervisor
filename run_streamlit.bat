@echo off
echo Starting Smart Building AI Assistant...
echo.
echo Make sure you have set your GROQ_API_KEY in the .env file
echo.
cd /d "d:\Supervisor"
streamlit run streamlit_app.py --server.port 8501 --server.headless false
pause

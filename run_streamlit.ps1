Write-Host "Starting Smart Building AI Assistant..." -ForegroundColor Green
Write-Host ""
Write-Host "Make sure you have set your GROQ_API_KEY in the .env file" -ForegroundColor Yellow
Write-Host ""

Set-Location "d:\Supervisor"

# Check if streamlit is installed
try {
    streamlit --version | Out-Null
    Write-Host "Streamlit found. Starting application..." -ForegroundColor Green
    streamlit run streamlit_app.py --server.port 8501 --server.headless false
} catch {
    Write-Host "Streamlit not found. Installing..." -ForegroundColor Red
    pip install streamlit
    Write-Host "Starting application..." -ForegroundColor Green
    streamlit run streamlit_app.py --server.port 8501 --server.headless false
}

Read-Host "Press Enter to exit"

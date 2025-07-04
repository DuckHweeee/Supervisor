@echo off
echo ============================================
echo Smart Building AI - Auto-Training System
echo ============================================
echo.
echo Choose an option:
echo 1. Train on IIC Document only
echo 2. Train on all documents (batch)
echo 3. Start auto-training watcher
echo 4. Show training status
echo 5. Run Streamlit app
echo 6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo Training on IIC document...
    python enhanced_training.py --iic
    pause
) else if "%choice%"=="2" (
    echo.
    echo Training on all documents...
    python enhanced_training.py --batch
    pause
) else if "%choice%"=="3" (
    echo.
    echo Starting auto-training watcher...
    echo Press Ctrl+C to stop
    python simple_auto_trainer.py
    pause
) else if "%choice%"=="4" (
    echo.
    echo Showing training status...
    python training_summary.py
    pause
) else if "%choice%"=="5" (
    echo.
    echo Starting Streamlit app...
    streamlit run streamlit_app.py
    pause
) else if "%choice%"=="6" (
    echo.
    echo Goodbye!
    exit
) else (
    echo.
    echo Invalid choice. Please try again.
    pause
)

goto :eof

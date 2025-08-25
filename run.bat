@echo off
echo Starting Meridian Demo...
echo.

call venv\Scripts\activate

echo Choose demo mode:
echo 1. Jupyter Notebook (Recommended)
echo 2. Streamlit Dashboard
echo.

set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo Launching Jupyter Lab...
    jupyter lab notebooks\01_Executive_Overview.ipynb
) else if "%choice%"=="2" (
    echo Launching Streamlit Dashboard...
    streamlit run app.py
) else (
    echo Invalid choice
)

pause

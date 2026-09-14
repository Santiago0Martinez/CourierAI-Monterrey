# CourierAI Automated Windows Setup Script
Write-Host "Setting up CourierAI Environment..." -ForegroundColor Green
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Write-Host "Environment ready! Run 'streamlit run Front-End/main.py' to launch UI." -ForegroundColor Cyan

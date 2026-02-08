@echo off
echo Starting Todo Backend Server...
cd /d "C:\Users\mehre\Downloads\hackathonnII\Hackathon_II\phase_III\backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
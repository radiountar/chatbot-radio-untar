@echo off
cd /d "%~dp0"
echo [Info] Mengaktifkan Virtual Environment...
call venv\Scripts\activate

echo [Info] Menjalankan Uvicorn Server...
uvicorn app.main:app --reload

pause



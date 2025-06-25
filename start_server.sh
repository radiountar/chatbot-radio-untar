#!/bin/bash

# Aktifkan virtual environment
source venv/bin/activate

# Jalankan Uvicorn server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# File: start_server_production.py

import uvicorn

def main():
    print("[Info] Menjalankan server FastAPI dalam mode Production...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # Biar server bisa diakses dari mana saja
        port=8000,        # Port default
        reload=False,     # Tidak ada auto-reload, cocok untuk produksi
        workers=4         # Jalankan 4 worker untuk performa lebih baik
    )

if __name__ == "__main__":
    main()

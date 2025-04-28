import os
import uvicorn

def main():
    # Aktifkan environment kalau perlu (opsional, biasanya sudah aktif manual)
    # os.system("venv\\Scripts\\activate")  # Tidak perlu di sini untuk Python script.

    print("[Info] Menjalankan Uvicorn Server...")
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main()



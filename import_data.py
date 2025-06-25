import os
import pandas as pd
import mysql.connector
from dotenv import load_dotenv

# ✅ Muat environment variable dari file .env
load_dotenv()

# ✅ Konfigurasi koneksi database dari environment
db_config = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

# ✅ Fungsi untuk import FAQ
def import_faq(filepath):
    try:
        df = pd.read_excel(filepath)
        df = df.dropna(subset=["Pertanyaan", "Jawaban"])

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM faq")

        for _, row in df.iterrows():
            cursor.execute(
                "INSERT INTO faq (pertanyaan, jawaban) VALUES (%s, %s)",
                (row['Pertanyaan'], row['Jawaban'])
            )

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Data FAQ berhasil diimport ke MySQL")
    except Exception as e:
        print(f"❌ Gagal mengimpor FAQ: {e}")

# ✅ Fungsi untuk import Lagu
def import_lagu(filepath):
    try:
        df = pd.read_excel(filepath)
        df = df.dropna(subset=["judul", "artist"])

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM lagu")

        for _, row in df.iterrows():
            cursor.execute(
                "INSERT INTO lagu (judul, artist) VALUES (%s, %s)",
                (row['judul'], row['artist'])
            )

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Data Lagu berhasil diimport ke MySQL")
    except Exception as e:
        print(f"❌ Gagal mengimpor Lagu: {e}")

# ✅ Jalankan fungsi jika file ini dijalankan langsung
if __name__ == "__main__":
    import_faq("dataset_radio_untar.xlsx")
    import_lagu("daftar_lagu.xlsx")

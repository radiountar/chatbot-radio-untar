import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# Konfigurasi database dari .env
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

def convert_excel_time_to_string(cell):
    if isinstance(cell, float) or isinstance(cell, int):
        jam = int(cell * 24)
        menit = int((cell * 24 * 60) % 60)
        return f"{jam:02d}:{menit:02d}"
    return str(cell)

def import_jadwal(filepath):
    try:
        df = pd.read_excel(filepath)

        df["jam_mulai"] = df["jam_mulai"].apply(convert_excel_time_to_string)
        df["jam_selesai"] = df["jam_selesai"].apply(convert_excel_time_to_string)

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM jadwal_siaran")

        for idx, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO jadwal_siaran (hari, jam_mulai, jam_selesai, nama_acara, penyiar)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    row['hari'].lower(),
                    row['jam_mulai'],
                    row['jam_selesai'],
                    row['nama_program'],
                    row['penyiar']
                ))
            except Exception as e:
                print(f"❌ Error parsing baris: {idx+1} | {e}")

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Jadwal siaran berhasil diimpor ke database.")

    except Exception as e:
        print(f"❌ Error koneksi / insert: {e}")

if __name__ == "__main__":
    import_jadwal("jadwal_siaran.xlsx")

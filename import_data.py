import pandas as pd
import mysql.connector

# Konfigurasi koneksi database MySQL
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",      # Ganti dengan password MySQL kamu
    "database": "radio_untar"
}

# Fungsi untuk import FAQ
def import_faq(filepath):
    try:
        df = pd.read_excel(filepath)

        # Hapus baris yang kolomnya kosong
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


# Fungsi untuk import Lagu
def import_lagu(filepath):
    try:
        df = pd.read_excel(filepath)
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Kosongkan isi tabel lagu terlebih dahulu (opsional)
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

# Jalankan fungsi
if __name__ == "__main__":
    import_faq("dataset_radio_untar.xlsx")
    import_lagu("daftar_lagu.xlsx")

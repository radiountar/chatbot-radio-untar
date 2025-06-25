import pandas as pd
from app.db import get_connection

def import_faq():
    try:
        # Load Excel
        df = pd.read_excel("dataset_radio_untar.xlsx")

        # Bersihkan data
        df = df.dropna(subset=["Pertanyaan", "Jawaban"])
        print(f"📄 {len(df)} baris data akan diimpor ke database.")

        # Koneksi ke MySQL
        conn = get_connection()
        cursor = conn.cursor()

        # Kosongkan tabel FAQ
        cursor.execute("DELETE FROM faq")
        print("🧹 Tabel 'faq' dikosongkan.")

        # Masukkan data
        for _, row in df.iterrows():
            cursor.execute(
                "INSERT INTO faq (pertanyaan, jawaban) VALUES (%s, %s)",
                (row["Pertanyaan"], row["Jawaban"])
            )

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Import selesai. FAQ berhasil diperbarui.")
    
    except Exception as e:
        print(f"❌ Gagal import FAQ: {e}")

if __name__ == "__main__":
    import_faq()

import pandas as pd
import mysql.connector

# Konfigurasi koneksi database
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "radio_untar"
}

# Baca file Excel
file_path = "jadwal_siaran.xlsx"
df = pd.read_excel(file_path, header=None)

# Format dan bersihkan data
data_bersih = []
for row in df[0]:
    try:
        parts = row.split(";")
        if len(parts) >= 5:
            hari = parts[0].strip().lower()
            jam_mulai = parts[1].strip().replace(".", ":")
            jam_selesai = parts[2].strip().replace(".", ":")
            nama_program = parts[3].strip()
            penyiar = parts[4].strip()
            data_bersih.append((hari, jam_mulai, jam_selesai, nama_program, penyiar))
    except Exception as e:
        print("❌ Error parsing baris:", row, "|", e)

# Koneksi ke MySQL dan validasi duplikat
try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO jadwal_siaran (hari, jam_mulai, jam_selesai, nama_program, penyiar)
        VALUES (%s, %s, %s, %s, %s)
    """

    total_inserted = 0

    for record in data_bersih:
        # Cek apakah record ini sudah ada di database
        cursor.execute("""
            SELECT COUNT(*) FROM jadwal_siaran
            WHERE hari=%s AND jam_mulai=%s AND jam_selesai=%s AND nama_program=%s
        """, (record[0], record[1], record[2], record[3]))
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.execute(insert_query, record)
            total_inserted += 1
        else:
            print(f"⚠️ Duplikat ditemukan, dilewati: {record}")

    conn.commit()
    print(f"\n✅ Berhasil menyimpan {total_inserted} data baru ke database.")

    cursor.close()
    conn.close()

except mysql.connector.Error as err:
    print("❌ Error koneksi / insert:", err)

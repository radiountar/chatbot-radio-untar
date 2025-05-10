from datetime import datetime
from app.db import get_connection

def siapa_siaran_sekarang():
    now = datetime.now()
    hari = now.strftime("%A").lower()
    jam_sekarang = now.strftime("%H.%M")

    conn = get_connection()
    cursor = conn.cursor()

    # Ambil semua jadwal untuk hari ini
    query = """
        SELECT nama_program, penyiar, jam_mulai, jam_selesai
        FROM jadwal_siaran
        WHERE LOWER(hari) = %s
        ORDER BY jam_mulai ASC
    """
    cursor.execute(query, (hari,))
    hasil = cursor.fetchall()

    # Cek apakah ada siaran yang sedang berlangsung
    for program, penyiar, mulai, selesai in hasil:
        if mulai <= jam_sekarang <= selesai:
            return f"🎙️ Saat ini sedang berlangsung program *{program}* bersama *{penyiar}* (pukul {mulai} - {selesai})"

    # Jika tidak ada siaran aktif, cari jadwal selanjutnya
    for program, penyiar, mulai, _ in hasil:
        if jam_sekarang < mulai:
            return f"📅 Saat ini belum ada siaran yang berlangsung. Jadwal terdekat adalah program *{program}* bersama *{penyiar}* pukul {mulai}."

    return "📻 Hari ini tidak ada lagi siaran yang tersisa. Silakan cek kembali besok 😊"


# Untuk pengujian langsung
if __name__ == "__main__":
    print(siapa_siaran_sekarang())

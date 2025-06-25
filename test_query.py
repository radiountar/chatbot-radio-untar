from app.db import get_connection

def cari_lagu_berdasarkan_artist(artist):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT id, judul, artist FROM lagu WHERE LOWER(artist) LIKE %s"
    value = "%" + artist.lower() + "%"
    cursor.execute(query, (value,))
    results = cursor.fetchall()

    cursor.close()
    conn.close()
    return results

if __name__ == "__main__":
    hasil = cari_lagu_berdasarkan_artist("taylor swift")
    if hasil:
        print("✅ Ditemukan lagu:")
        for row in hasil:
            print(row)
    else:
        print("❌ Tidak ditemukan lagu.")

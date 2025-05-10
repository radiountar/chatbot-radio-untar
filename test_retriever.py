from app.lagu_retriever import LaguRetriever

retriever = LaguRetriever()

while True:
    query = input("🔍 Cari lagu: ")
    if query.lower() in ["exit", "keluar"]:
        break

    results = retriever.cari_lagu_terdekat(query)

    if not results:
        print("❌ Tidak ditemukan.")
    else:
        print("🎵 Hasil:")
        for i, (judul, artist, skor) in enumerate(results, 1):
            print(f"{i}. {judul} - {artist} (skor: {skor})")

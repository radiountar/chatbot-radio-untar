from app.scraper_artikel import get_latest_articles

artikel = get_latest_articles()

if not artikel:
    print("❌ Tidak ditemukan artikel.")
else:
    print("📰 Artikel Terbaru:")
    for i, (judul, link) in enumerate(artikel, 1):
        print(f"{i}. {judul} — {link}")

import requests
from bs4 import BeautifulSoup

def get_latest_articles(limit=5):
    url = "https://streaming.radiountar.com/category/news-article/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Gagal mengambil artikel: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    articles = []

    # Struktur WordPress: <article> > h2.entry-title > a
    for item in soup.select("article h2.entry-title a")[:limit]:
        judul = item.get_text(strip=True)
        link = item.get("href")
        if judul and link:
            articles.append((judul, link))

    return articles

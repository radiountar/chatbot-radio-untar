import requests
from bs4 import BeautifulSoup
import re

# Langsung dari link podcast kamu
PODCAST_URL = "https://open.spotify.com/show/3TXqKLvEojGoCOHUfTy7SQ"

def get_latest_episodes(limit=5):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(PODCAST_URL, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Gagal akses Spotify podcast: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=re.compile(r"/episode/"))
    seen = set()
    results = []

    for link in links:
        href = link.get("href")
        title = link.get_text(strip=True)
        if href and title and href not in seen:
            results.append((title, "https://open.spotify.com" + href))
            seen.add(href)
        if len(results) >= limit:
            break

    return results


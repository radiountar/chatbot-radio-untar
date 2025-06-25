import requests
from bs4 import BeautifulSoup

def get_latest_articles(jumlah=5):
    try:
        url = "https://streaming.radiountar.com/blog/"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        articles = []
        posts = soup.find_all("article", limit=jumlah)
        
        for post in posts:
            title_tag = post.find("h2", class_="entry-title")
            if title_tag and title_tag.a:
                title = title_tag.text.strip()
                link = title_tag.a.get("href")
                articles.append((title, link))

        return articles

    except Exception as e:
        print(f"[ERROR artikel] {e}")
        return []

# Untuk testing langsung
if __name__ == "__main__":
    hasil = get_latest_articles()
    for i, (judul, link) in enumerate(hasil, 1):
        print(f"{i}. {judul} => {link}")

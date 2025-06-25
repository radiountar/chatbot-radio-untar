import feedparser

def get_latest_episodes(jumlah=5):
    try:
        url = "https://anchor.fm/s/324dbf84/podcast/rss"
        feed = feedparser.parse(url)

        episodes = []
        for entry in feed.entries[:jumlah]:
            title = entry.title
            link = entry.link
            episodes.append((title, link))

        return episodes

    except Exception as e:
        print(f"[ERROR podcast] {e}")
        return []

# Untuk testing langsung
if __name__ == "__main__":
    hasil = get_latest_episodes()
    for i, (judul, link) in enumerate(hasil, 1):
        print(f"{i}. {judul} => {link}")

from fastapi import FastAPI
from pydantic import BaseModel
from app.chatbot import Chatbot
from app.telegram_notifier import send_telegram_notification
from app.lagu_request_handler import handle_request_input, user_sessions
from app.scraper_artikel import get_latest_articles
from app.scraper_podcast import get_latest_episodes
from app.evaluation import log_interaction
from app.jadwal_checker import siapa_siaran_sekarang
import re

app = FastAPI()

# DB Config
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "radio_untar"
}

chatbot = Chatbot(db_config)
PENYIAR_CHAT_ID = "123456789"

class Message(BaseModel):
    user_id: str
    message: str

# ================================
# INTENT DETECTION
# ================================
def is_feedback(msg: str) -> bool:
    return msg.strip().lower() in ["ya", "iya", "tidak", "nggak", "gak", "yes", "no"]

def is_article_request(msg: str) -> bool:
    return any(k in msg.lower() for k in ["artikel", "berita", "postingan", "tulisan"])

def is_podcast_request(msg: str) -> bool:
    return "podcast" in msg.lower()

def is_jadwal_siaran_request(msg: str) -> bool:
    msg = msg.lower()
    return any(kw in msg for kw in [
        "siapa yang siaran", "siapa penyiar", "siaran sekarang", "sedang siaran", "penyiar saat ini"
    ])

def is_song_request(msg: str) -> bool:
    msg = msg.lower()
    patterns = [
        r"\b(request|minta|putar|mainkan|dengarkan|play)\b.*\blagu\b",
        r"\blagu\b.*\b(request|minta|putar|mainkan|dengarkan|play)\b",
        r"\b(request|minta|putar|mainkan|dengarkan|play)\b\s+[a-zA-Z ]+$"
    ]
    return any(re.search(p, msg) for p in patterns)

# ================================
# CHAT ENDPOINT
# ================================
@app.post("/chat")
async def chat_endpoint(payload: Message):
    user_id = payload.user_id
    user_message = payload.message.strip().lower()
    print(f"[DEBUG] Pesan masuk: {user_message} dari {user_id}")

    # 1. Feedback evaluasi
    if user_id in user_sessions and user_sessions[user_id].get("state") == "menunggu_feedback":
        rating = 5 if "ya" in user_message else 1
        last_q = user_sessions[user_id]["pertanyaan"]
        last_a = user_sessions[user_id]["jawaban"]
        rank = user_sessions[user_id]["rank"]
        log_interaction(last_q, last_a, rank, rating)
        del user_sessions[user_id]
        return {"response": "Terima kasih atas feedback-nya! 🙏"}

    # 2. Artikel
    if is_article_request(user_message):
        hasil = get_latest_articles()
        if not hasil:
            return {"response": "Maaf, tidak dapat mengambil artikel terbaru saat ini."}
        return {
            "response": "📰 Artikel Terbaru",
            "data": [{"no": i, "judul": j, "link": l} for i, (j, l) in enumerate(hasil, 1)]
        }

    # 3. Podcast
    if is_podcast_request(user_message):
        hasil = get_latest_episodes()
        if not hasil:
            return {"response": "Maaf, tidak menemukan episode podcast terbaru."}
        return {
            "response": "🎧 Episode Podcast Terbaru",
            "data": [{"no": i, "judul": j, "link": l} for i, (j, l) in enumerate(hasil, 1)]
        }

    # 4. Jadwal siaran sekarang
    if is_jadwal_siaran_request(user_message):
        response = siapa_siaran_sekarang()
        return {"response": response}

    # 5. Permintaan Lagu
    if is_song_request(user_message):
        response, lagu_info = handle_request_input(user_id, user_message)
        if isinstance(response, dict) and "data" in response:
            return response
        elif lagu_info:
            send_telegram_notification(f"📻 Permintaan lagu:\n{lagu_info}", chat_id=PENYIAR_CHAT_ID)
            return {"response": response}
        elif isinstance(response, str):
            return {"response": response}

    # 6. FAQ + evaluasi
    jawaban, indeks = chatbot.get_answer(user_message)
    user_sessions[user_id] = {
        "state": "menunggu_feedback",
        "pertanyaan": user_message,
        "jawaban": jawaban,
        "rank": indeks
    }
    return {"response": jawaban + "\n\n🙏 Apakah jawaban saya membantu? (ya/tidak)"}

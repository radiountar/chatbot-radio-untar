from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.chatbot import Chatbot
from app.telegram_notifier import send_telegram_notification
from app.lagu_request_handler import handle_request_input, handle_selection_input, user_sessions
from app.scraper_artikel import get_latest_articles
from app.scraper_podcast import get_latest_episodes
from app.evaluation import log_interaction
from dotenv import load_dotenv
import os
import re

load_dotenv()

app = FastAPI()

# Aktifkan CORS agar bisa diakses dari chat.html atau WordPress
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chatbot = Chatbot()
PENYIAR_CHAT_ID = os.getenv("CHAT_ID")

class Message(BaseModel):
    user_id: str
    message: str

# ======== Fungsi Deteksi Kategori Pesan =========

def is_feedback(msg: str) -> bool:
    return msg.strip().lower() in ["ya", "iya", "tidak", "nggak", "gak", "yes", "no"]

def is_article_request(msg: str) -> bool:
    return any(k in msg.lower() for k in ["artikel", "berita", "postingan", "tulisan"])

def is_podcast_request(msg: str) -> bool:
    return "podcast" in msg.lower()

def is_song_request(msg: str) -> bool:
    msg = msg.lower()
    patterns = [
        r"\b(request|minta|putar|mainkan|dengarkan|play)\b.*\blagu\b",
        r"\blagu\b.*\b(request|minta|putar|mainkan|dengarkan|play)\b",
        r"\b(request|minta|putar|mainkan|dengarkan|play)\b\s+[a-zA-Z ]+$"
    ]
    return any(re.search(p, msg) for p in patterns) or "lagu" in msg

# ========== Endpoint Utama Chatbot ==========

@app.post("/chat")
async def chat_endpoint(payload: Message):
    user_id = payload.user_id
    user_message = payload.message.strip().lower()
    print(f"[DEBUG] Pesan masuk: {user_message} dari {user_id}")

    try:
        # Feedback evaluasi
        if user_id in user_sessions and user_sessions[user_id].get("state") == "menunggu_feedback":
            rating = 5 if "ya" in user_message else 1
            last_q = user_sessions[user_id]["pertanyaan"]
            last_a = user_sessions[user_id]["jawaban"]
            rank = user_sessions[user_id]["rank"]
            log_interaction(last_q, last_a, rank, rating)
            del user_sessions[user_id]
            return {"response": "Terima kasih atas feedback-nya! 🙏"}

        # Pemilihan lagu setelah rekomendasi
        if user_id in user_sessions and user_sessions[user_id].get("state") == "menunggu_pilihan":
            response, info = handle_selection_input(user_id, user_message)
            if info:
                send_telegram_notification(f"📻 Permintaan lagu:\n{info}", chat_id=PENYIAR_CHAT_ID)
            return {"response": response.encode('utf-8', 'replace').decode('utf-8')}

        # Artikel
        if is_article_request(user_message):
            if user_id in user_sessions:
                del user_sessions[user_id]
            hasil = get_latest_articles()
            if not hasil:
                return {"response": "Maaf, tidak dapat mengambil artikel terbaru saat ini."}
            response = "📰 Artikel Terbaru\n" + "\n".join([f"{i}. {j} => {l}" for i, (j, l) in enumerate(hasil, 1)])
            return {"response": response.encode('utf-8', 'replace').decode('utf-8')}

        # Podcast
        if is_podcast_request(user_message):
            if user_id in user_sessions:
                del user_sessions[user_id]
            hasil = get_latest_episodes()
            if not hasil:
                return {"response": "Maaf, tidak menemukan episode podcast terbaru."}
            response = "🎧 Episode Podcast Terbaru\n" + "\n".join([f"{i}. {j} => {l}" for i, (j, l) in enumerate(hasil, 1)])
            return {"response": response.encode('utf-8', 'replace').decode('utf-8')}

        # Permintaan Lagu
        if is_song_request(user_message):
            # Hapus sesi lagu sebelumnya jika ada
            if user_id in user_sessions and user_sessions[user_id].get("state") == "menunggu_pilihan":
                del user_sessions[user_id]
            response, lagu_info = handle_request_input(user_id, user_message)
            return {"response": response.encode('utf-8', 'replace').decode('utf-8')}

        # FAQ
        jawaban, indeks = chatbot.get_answer(user_message)
        user_sessions[user_id] = {
            "state": "menunggu_feedback",
            "pertanyaan": user_message,
            "jawaban": jawaban,
            "rank": indeks
        }
        response = jawaban + "\n\n🙏 Apakah jawaban saya membantu? (ya/tidak)"
        return {"response": response.encode('utf-8', 'replace').decode('utf-8')}

    except Exception as e:
        print(f"[ERROR] {e}")
        return {"response": "Maaf, terjadi kesalahan internal pada server."}

# app/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.chatbot import Chatbot
from app.evaluation import logs, log_interaction, calculate_mrr, calculate_user_satisfaction
from app.telegram_notifier import send_telegram_notification
from dotenv import load_dotenv
load_dotenv()


app = FastAPI()

# Inisialisasi chatbot
try:
    chatbot = Chatbot("dataset_radio_untar.xlsx")
except Exception as e:
    print(f"❌ Gagal inisialisasi Chatbot: {e}")
    raise e

# Struktur pertanyaan dari user
class QuestionData(BaseModel):
    question: str
    user_id: str
    rating: int

# Endpoint utama
@app.post("/ask")
def ask_question(data: QuestionData):
    try:
        answer, rank = chatbot.get_answer(data.question)

        # Kirim notifikasi ke Telegram kalau mengandung kata "lagu"
        if "lagu" in data.question.lower() and any(kata in data.question.lower() for kata in ["minta", "request", "putar"]):
            send_telegram_notification(
                f"🎵 Permintaan Lagu Baru!\n\n📩 {data.question}\n👤 ID: {data.user_id}"
            )

        # Simpan log evaluasi
        log_interaction(data.question, answer, rank, data.rating)

        # Hitung evaluasi
        mrr_score = calculate_mrr(logs)
        avg_rating = calculate_user_satisfaction(logs)

        return {
            "question": data.question,
            "answer": answer,
            "rank": int(rank),           # ✅ Fix disini
            "rating": data.rating,
            "mrr": round(mrr_score, 3),
            "user_satisfaction": round(avg_rating, 2)
        }

    except Exception as e:
        print(f"❌ Terjadi error saat memproses pertanyaan: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



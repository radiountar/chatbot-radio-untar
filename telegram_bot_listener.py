import os
import re
import telebot
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from app.chatbot import Chatbot
from app.lagu_request_handler import handle_request_input, handle_selection_input, user_sessions
from app.db import get_connection
from app.evaluation import log_interaction
from app.telegram_notifier import send_telegram_notification
from app.dataset_filter import load_kata_kasar_xlsx, buat_regex_kata_kasar, cek_kata_kasar_dari_xlsx

# ========== Persiapan Awal ==========
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Bot pengguna
NOTIF_TOKEN = os.getenv("NOTIF_TOKEN")        # Bot penyiar
NOTIF_CHAT_ID = os.getenv("NOTIF_CHAT_ID")    # Chat ID penyiar

bot = telebot.TeleBot(TELEGRAM_TOKEN)
chatbot = Chatbot()

# ========== Data Lagu dan TF-IDF ==========
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT judul, artist FROM lagu")
rows = cursor.fetchall()
song_data = [{'judul': row[0], 'penyanyi': row[1]} for row in rows]

def preprocess(text):
    return re.sub(r'\W+', ' ', text.lower()).strip()

corpus = [preprocess(f"{d['judul']} {d['penyanyi']}") for d in song_data]
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(corpus)

# ========== Data Kata Kasar ==========
kata_kasar = load_kata_kasar_xlsx()
kata_kasar_pattern = buat_regex_kata_kasar(kata_kasar)

# ========== Handler Pesan ==========
@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    text = message.text.strip().lower()

    # 🚫 Filtering kata kasar
    if cek_kata_kasar_dari_xlsx(text, kata_kasar_pattern):
        bot.reply_to(message, "🚫 Mohon gunakan bahasa yang sopan saat berinteraksi dengan bot ini.")
        return

    # 🟢 Sambutan Awal
    if text in ["/start", "halo", "hi", "mulai"]:
        bot.reply_to(message, "👋 Halo! Saya adalah Chatbot Radio Untar.\n\nSaya bisa bantu menjawab tentang:\n✅ FAQ seputar Radio Untar\n🎵 Permintaan lagu\n📰 Artikel terbaru\n🎧 Podcast terbaru\n\nSilakan ketik pertanyaan Anda!")
        return

    # 🎵 Pilihan lagu
    if user_id in user_sessions and user_sessions[user_id].get("state") == "menunggu_pilihan":
        response, info = handle_selection_input(user_id, text)
        bot.reply_to(message, response)
        if info:
            send_telegram_notification(f"📻 Permintaan lagu:\n{info}", chat_id=NOTIF_CHAT_ID, token=NOTIF_TOKEN)
            log_interaction(f"Permintaan lagu: {info}", "Dikirim ke penyiar", rank=0, rating=5)
        return

    # 📊 Feedback pengguna
    if user_id in user_sessions and user_sessions[user_id].get("state") == "menunggu_feedback":
        if text in ["ya", "iya", "yes"]:
            last_q = user_sessions[user_id]["pertanyaan"]
            last_a = user_sessions[user_id]["jawaban"]
            rank = user_sessions[user_id]["rank"]
            log_interaction(last_q, last_a, rank, 5)
            del user_sessions[user_id]
            bot.reply_to(message, "🙏 Terima kasih, senang bisa membantu! Jika ada pertanyaan lain, silakan ditanyakan.")
            return
        elif text in ["tidak", "gak", "nggak", "no"]:
            last_q = user_sessions[user_id]["pertanyaan"]
            last_a = user_sessions[user_id]["jawaban"]
            rank = user_sessions[user_id]["rank"]
            log_interaction(last_q, last_a, rank, 1)
            del user_sessions[user_id]
            bot.reply_to(message, "🙏 Terima kasih atas masukannya! Kami akan terus berusaha memberikan jawaban yang lebih baik.")
            return
        else:
            # Anggap pertanyaan baru
            del user_sessions[user_id]

    # 📰 Artikel terbaru
    if "artikel" in text or "berita" in text:
        from app.scraper_artikel import get_latest_articles
        hasil = get_latest_articles()
        if not hasil:
            bot.reply_to(message, "Maaf, tidak dapat mengambil artikel terbaru.")
        else:
            jawaban = "📰 Artikel Terbaru\n" + "\n".join([f"{i+1}. {j} => {l}" for i, (j, l) in enumerate(hasil)])
            log_interaction(text, jawaban, rank=0, rating=5)
            bot.reply_to(message, jawaban)
        return

    # 🎧 Podcast terbaru
    if "podcast" in text:
        from app.scraper_podcast import get_latest_episodes
        hasil = get_latest_episodes()
        if not hasil:
            bot.reply_to(message, "Maaf, tidak dapat mengambil podcast.")
        else:
            jawaban = "🎧 Podcast Terbaru\n" + "\n".join([f"{i+1}. {j} => {l}" for i, (j, l) in enumerate(hasil)])
            log_interaction(text, jawaban, rank=0, rating=5)
            bot.reply_to(message, jawaban)
        return

    # 🎵 Permintaan lagu
    if "lagu" in text or any(k in text for k in ["mainkan", "putar", "minta", "play"]):
        response, _ = handle_request_input(
            user_id, text, cursor, conn, vectorizer, tfidf_matrix, song_data
        )
        log_interaction(text, response, rank=0, rating=5)
        bot.reply_to(message, response)
        return

    # 💬 Fallback: FAQ
    jawaban, indeks = chatbot.get_answer(text)
    if indeks == -1:
        response = "🤖 Maaf, saya hanya bisa menjawab pertanyaan yang berkaitan dengan Radio Untar."
        log_interaction(text, response, rank=-1, rating=0)
        bot.reply_to(message, response)
        return

    user_sessions[user_id] = {
        "state": "menunggu_feedback",
        "pertanyaan": text,
        "jawaban": jawaban,
        "rank": indeks
    }
    log_interaction(text, jawaban, indeks, 0)
    bot.reply_to(message, jawaban + "\n\n🙏 Apakah jawaban saya membantu? (ya/tidak)")

# ========== Menjalankan Bot ==========
print("🤖 Telegram chatbot sedang berjalan...")
bot.infinity_polling()

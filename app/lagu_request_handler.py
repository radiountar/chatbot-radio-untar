from app.db import get_connection
from app.lagu_retriever import LaguRetriever
from nltk.corpus import wordnet
import re

# Menyimpan sesi pengguna
user_sessions = {}
retriever = LaguRetriever()

# 🔍 Filtering input
def preprocess(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def replace_synonyms(text: str) -> str:
    words = text.split()
    new_words = []
    for word in words:
        syns = wordnet.synsets(word)
        if syns:
            lemma = syns[0].lemmas()[0].name().replace("_", " ")
            new_words.append(lemma)
        else:
            new_words.append(word)
    return ' '.join(new_words)

def extract_artist_from_message(message: str) -> str:
    # Hilangkan kata-kata umum
    keywords = ["request", "lagu", "minta", "putar", "mainkan", "aku", "saya", "mau", "denger", "dengarkan", "musik", "dong", "tolong"]
    message = preprocess(message)
    message = replace_synonyms(message)
    for word in keywords:
        message = message.replace(word, "")
    return message.strip()

# 🔁 Fallback jika retriever gagal
def fallback_sql_search(artist_keyword: str):
    print(f"[DEBUG] Fallback SQL: Mencari '{artist_keyword}' langsung di DB.")
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT id, judul, artist FROM lagu WHERE LOWER(artist) LIKE %s"
    query_value = "%" + artist_keyword.lower() + "%"
    cursor.execute(query, (query_value,))
    results = cursor.fetchall()

    cursor.close()
    conn.close()
    return [(judul, artist, 1.0) for _, judul, artist in results]

# 🔁 Fungsi utama
def handle_request_input(chat_id, user_input):
    # Tahap 1: user memilih nomor lagu
    if chat_id in user_sessions and user_sessions[chat_id].get("state") == "menunggu_pilihan":
        pilihan = user_input.strip()
        daftar = user_sessions[chat_id]["daftar_lagu"]
        if pilihan.isdigit():
            idx = int(pilihan) - 1
            if 0 <= idx < len(daftar):
                judul, artist = daftar[idx]
                del user_sessions[chat_id]
                return f"✅ Permintaan lagu *{judul}* oleh *{artist}* telah dikirim ke penyiar.", f"{judul} - {artist}"
        return "❌ Pilihan tidak valid. Silakan masukkan angka dari daftar lagu.", None

    # Tahap 2: ekstrak keyword dan cari
    keyword = extract_artist_from_message(user_input)
    hasil = retriever.cari_lagu_terdekat(keyword)

    if not hasil:
        hasil = fallback_sql_search(keyword)
        if not hasil:
            return "Maaf, tidak ditemukan lagu yang cocok dengan pencarian Anda.", None

    user_sessions[chat_id] = {
        "state": "menunggu_pilihan",
        "daftar_lagu": [(judul, artist) for judul, artist, _ in hasil]
    }

    daftar_lagu = [
        {"no": i, "judul": judul}
        for i, (judul, _) in enumerate(user_sessions[chat_id]["daftar_lagu"], 1)
    ]

    return {
        "response": "🎵 Berikut daftar lagu yang ditemukan",
        "data": daftar_lagu,
        "note": "Silakan balas dengan angka pilihanmu:"
    }, None

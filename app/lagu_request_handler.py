import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.db import get_connection

# Sesi pengguna disimpan global
user_sessions = {}

def bersihkan_kalimat(teks):
    teks = teks.lower()
    teks = re.sub(r'[^\w\s]', '', teks)
    stopwords = ['lagu', 'putar', 'mainkan', 'dengarkan', 'request', 'minta', 'play']
    for word in stopwords:
        teks = teks.replace(word, '')
    return teks.strip()

def handle_request_input(user_id, user_message, cursor, conn, vectorizer, tfidf_matrix, song_data):
    query = bersihkan_kalimat(user_message)
    print(f"[DEBUG] Query bersih: {query}")

    query_vec = vectorizer.transform([query])
    similarities = cosine_similarity(query_vec, tfidf_matrix)[0]
    print(f"[DEBUG] Skor tertinggi TF-IDF: {max(similarities)}")

    # Ambang batas minimal kecocokan
    threshold = 0.3

    if max(similarities) < threshold:
        return "Maaf, lagu yang Anda cari tidak tersedia. Silakan coba dengan judul atau penyanyi lain.", None

    # Ambil top 30 hasil teratas
    top_indices = similarities.argsort()[::-1][:30]
    pilihan_mentah = [song_data[i] for i in top_indices]

    # Filter hasil yang cocok
    hasil_filter = [
        lagu for lagu in pilihan_mentah
        if query in lagu["judul"].lower() or query in lagu["penyanyi"].lower()
    ]

    hasil_final = hasil_filter if hasil_filter else pilihan_mentah[:5]

    if not hasil_final:
        return "Maaf, saya tidak menemukan lagu yang cocok dengan permintaan Anda.", None

    user_sessions[user_id] = {
        "state": "menunggu_pilihan",
        "hasil_lagu": hasil_final
    }

    response = "🎵 Berikut lagu yang cocok:\n"
    for i, lagu in enumerate(hasil_final, 1):
        response += f"{i}. {lagu['judul']} - {lagu['penyanyi']}\n"
    response += "\nSilakan pilih nomor lagu yang Anda inginkan."

    return response, None

def handle_selection_input(user_id, user_message):
    if user_id not in user_sessions or user_sessions[user_id].get("state") != "menunggu_pilihan":
        return "Silakan ketik permintaan lagu terlebih dahulu.", None

    try:
        index = int(user_message.strip()) - 1
        lagu = user_sessions[user_id]["hasil_lagu"][index]
        info = f"{lagu['judul']} oleh {lagu['penyanyi']}"
        del user_sessions[user_id]
        return f"✅ Permintaan lagu '{info}' telah dicatat dan diteruskan ke penyiar.", info

    except (ValueError, IndexError):
        return "Nomor pilihan tidak valid. Silakan pilih nomor lagu yang tersedia.", None

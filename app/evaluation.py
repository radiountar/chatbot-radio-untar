import pandas as pd
import os
from datetime import datetime

# Path file log
LOG_FILE = "logs/chatbot_logs.xlsx"

# Pastikan folder logs tersedia
os.makedirs("logs", exist_ok=True)

# Fungsi menyimpan satu interaksi ke file XLSX (append)
def log_interaction(question: str, answer: str, rank: int, rating: int):
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": question,
        "answer": answer,
        "rank": rank,
        "rating": rating
    }

    try:
        if os.path.exists(LOG_FILE):
            # Jika file ada, baca dulu isinya lalu tambahkan
            existing_df = pd.read_excel(LOG_FILE)
            df = pd.concat([existing_df, pd.DataFrame([log_entry])], ignore_index=True)
        else:
            # Jika belum ada, buat baru
            df = pd.DataFrame([log_entry])

        # Simpan ke Excel
        df.to_excel(LOG_FILE, index=False)
        print("✅ Log disimpan ke", LOG_FILE)
    except Exception as e:
        print("❌ Gagal menyimpan log:", e)

# Fungsi untuk menghitung MRR
def calculate_mrr(logs_data):
    reciprocal_ranks = [1 / entry["rank"] for entry in logs_data if entry["rank"] > 0]
    return sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0

# Fungsi untuk menghitung rata-rata kepuasan
def calculate_user_satisfaction(logs_data):
    ratings = [entry["rating"] for entry in logs_data]
    return sum(ratings) / len(ratings) if ratings else 0

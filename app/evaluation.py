# app/evaluation.py

import pandas as pd
import os

# digunakan untuk menyimpan log
LOG_FILE = "logs/chatbot_logs.csv"

# untuk melihat Cek apakah folder logs sudah ada
os.makedirs("logs", exist_ok=True)

# List untuk menyimpan log sementara
logs = []

# menyimpan 1 interaksi ke logs
def log_interaction(question: str, answer: str, rank: int, rating: int):
    logs.append({
        "question": question,
        "answer": answer,
        "rank": rank,
        "rating": rating
    })
    save_logs_to_csv()

# simpan semua logs ke file CSV
def save_logs_to_csv():
    df = pd.DataFrame(logs)
    df.to_csv(LOG_FILE, index=False)
    print("✅ Log terbaru berhasil disimpan ke", LOG_FILE)

# Fungsi untuk hitung Mean Reciprocal Rank (MRR)
def calculate_mrr(logs_data):
    reciprocal_ranks = []
    for entry in logs_data:
        if entry["rank"] > 0:
            reciprocal_ranks.append(1 / entry["rank"])
    return sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0

# Fungsi untuk hitung rata-rata User Satisfaction
def calculate_user_satisfaction(logs_data):
    ratings = [entry["rating"] for entry in logs_data]
    return sum(ratings) / len(ratings) if ratings else 0


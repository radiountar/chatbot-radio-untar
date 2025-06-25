import pandas as pd
from datetime import datetime, timedelta
from app.evaluation import calculate_mrr, calculate_user_satisfaction

# Path ke file log utama dan file output
LOG_FILE = "logs/chatbot_logs.csv"
SUMMARY_FILE = "logs/summary_report.csv"

# Baca file log
try:
    df = pd.read_csv(LOG_FILE)
except FileNotFoundError:
    print("❌ File log tidak ditemukan.")
    exit()

# Pastikan kolom timestamp berbentuk datetime
if 'timestamp' not in df.columns:
    print("❌ Kolom timestamp tidak tersedia.")
    exit()

df['timestamp'] = pd.to_datetime(df['timestamp'])

# Filter data hanya 7 hari terakhir
one_week_ago = datetime.now() - timedelta(days=7)
weekly_data = df[df['timestamp'] >= one_week_ago]

if weekly_data.empty:
    print("⚠️ Tidak ada data interaksi dalam 7 hari terakhir.")
    exit()

# Hitung metrik evaluasi mingguan
mrr = calculate_mrr(weekly_data.to_dict(orient="records"))
satisfaction = calculate_user_satisfaction(weekly_data.to_dict(orient="records"))
total_questions = len(weekly_data)

# Buat ringkasan sebagai DataFrame
summary = pd.DataFrame([{
    "week_start": one_week_ago.strftime("%Y-%m-%d"),
    "week_end": datetime.now().strftime("%Y-%m-%d"),
    "total_questions": total_questions,
    "mean_reciprocal_rank": round(mrr, 4),
    "user_satisfaction": round(satisfaction, 2)
}])

# Simpan ke file summary
summary.to_csv(SUMMARY_FILE, index=False)
print("✅ Ringkasan evaluasi mingguan disimpan di:", SUMMARY_FILE)
print(summary)

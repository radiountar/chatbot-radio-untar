# app/telegram_notifier.py

import requests

# Ganti token dan chat_id sesuai data kamu
TELEGRAM_TOKEN = "7555977363:AAFUXIEmLya1HWmYNUA7N4NDpAYFWKqWJWM"
CHAT_ID = "8099488412"  # ID user kamu

def send_telegram_notification(message: str):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("[Telegram] Token atau Chat ID belum diset.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("[Telegram] Notifikasi berhasil dikirim.")
        else:
            print(f"[Telegram] Gagal kirim notifikasi. Status code: {response.status_code}")
    except Exception as e:
        print(f"[Telegram] Error saat kirim notifikasi: {e}")

# Uji manual (bisa hapus di production)
if __name__ == "__main__":
    send_telegram_notification("🚀 Bot Radio Untar sudah aktif!")



import requests

def send_telegram_notification(pesan, token, chat_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": pesan}

    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"❌ Gagal mengirim notifikasi Telegram: {response.text}")
        else:
            print("✅ Notifikasi Telegram berhasil dikirim.")
    except Exception as e:
        print(f"❌ Error saat mengirim Telegram: {e}")

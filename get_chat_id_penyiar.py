import os
import telebot
from dotenv import load_dotenv

load_dotenv(".env.penyiar")  # Ganti jika perlu

TOKEN = os.getenv("NOTIF_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def get_chat_id(message):
    print(f"✅ Chat ID penyiar: {message.chat.id}")

print("📨 Kirim pesan ke bot penyiar sekarang...")
bot.infinity_polling()

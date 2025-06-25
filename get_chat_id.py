import telebot

TOKEN = "7725242277:AAF10eicJ1GVXuir5aw95WCCywwPrsQXeUg"  # token bot penyiar

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda msg: True)
def handle(msg):
    print(f"✅ Chat ID kamu adalah: {msg.chat.id}")
    bot.reply_to(msg, "Chat ID kamu sudah dicatat.")

print("🔍 Silakan kirim pesan ke bot sekarang...")
bot.polling()

from app.lagu_request_handler import handle_request_input

# Gunakan ID tetap untuk menyimpan sesi
user_id = "user001"

print("🎙️ Chatbot Radio Untar — Mode Interaktif")
print("Ketik 'exit' untuk keluar.\n")

while True:
    user_message = input("🧑 Kamu: ").strip()
    
    if user_message.lower() in ["exit", "keluar"]:
        print("👋 Keluar dari chatbot.")
        break

    response, lagu_info = handle_request_input(user_id, user_message)

    print("🤖 Bot :", response)

    if lagu_info:
        print(f"📲 Notifikasi ke penyiar: {lagu_info}")

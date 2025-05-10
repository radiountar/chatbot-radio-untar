import requests

url = "http://127.0.0.1:8000/chat"

# Ganti pesan di bawah ini sesuai yang ingin kamu uji
data = {
    "user_id": "user001",
    "message": "siapa yang siaran sekarang?"
    # Contoh lain:
    # "message": "request lagu taylor swift"
    # "message": "artikel terbaru apa?"
    # "message": "apa itu radio untar?"
    # "message": "ya"
}

response = requests.post(url, json=data)

print("📤 Pertanyaan:", data["message"])
print("📡 Status:", response.status_code)
print("💬 Response:", response.json())

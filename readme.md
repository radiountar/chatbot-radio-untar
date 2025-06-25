# 🎙️ Chatbot Radio Untar - Retrieval Based

## Deskripsi
Ini adalah chatbot berbasis retrieval untuk Radio Untar, yang menjawab pertanyaan dari dataset dan mengirim notifikasi Telegram saat ada permintaan lagu.

## Fitur
- Retrieval FAQ menggunakan TF-IDF + Cosine Similarity
- Notifikasi ke Telegram jika ada permintaan lagu
- Evaluasi menggunakan MRR dan User Satisfaction Score

## Instalasi

1. **Clone Repo / Salin Folder**
2. **Aktifkan Virtual Environment**
   ```bash
   .\venv\Scripts\activate

pip install -r requirements.txt

python app/setup_nltk.py

uvicorn app.main:app --reload

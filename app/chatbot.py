import re
import pandas as pd
from nltk.corpus import wordnet
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.db import get_connection

def preprocess(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def replace_synonyms(text: str) -> str:
    words = text.split()
    new_words = []
    for word in words:
        syns = wordnet.synsets(word)
        if syns:
            lemma = syns[0].lemmas()[0].name().replace("_", " ")
            new_words.append(lemma)
        else:
            new_words.append(word)
    return ' '.join(new_words)

class Chatbot:
    def __init__(self, db_config):
        try:
            self.conn = get_connection()
            self.cursor = self.conn.cursor()
            self.cursor.execute("SELECT pertanyaan, jawaban FROM faq")
            rows = self.cursor.fetchall()
            self.dataset = pd.DataFrame(rows, columns=["Pertanyaan", "Jawaban"])
            print("✅ Dataset FAQ berhasil dimuat dari database.")
        except Exception as e:
            raise ValueError(f"Gagal membaca FAQ dari database: {e}")

        self.dataset = self.dataset.dropna(subset=["Pertanyaan", "Jawaban"])
        self.questions = self.dataset["Pertanyaan"].astype(str).tolist()
        self.answers = self.dataset["Jawaban"].astype(str).tolist()

        self.vectorizer = TfidfVectorizer()
        self.cleaned_questions = [replace_synonyms(preprocess(q)) for q in self.questions]
        self.tfidf_matrix = self.vectorizer.fit_transform(self.cleaned_questions)
        print("✅ Vectorizer dan matrix TF-IDF berhasil dibuat.")

    def get_answer(self, query: str) -> tuple[str, int]:
        cleaned_query = replace_synonyms(preprocess(query))
        query_vec = self.vectorizer.transform([cleaned_query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        best_match_idx = similarities.argmax()
        best_score = similarities[best_match_idx]

        if best_score < 0.2:
            return "Maaf, saya tidak mengerti pertanyaan Anda.", -1
        return self.answers[best_match_idx], best_match_idx + 1

import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import wordnet

class Chatbot:
    def __init__(self, dataset_path: str):
        try:
            self.dataset = pd.read_excel(dataset_path)
            print(f"✅ Dataset berhasil dibaca: {dataset_path}")
        except Exception as e:
            raise ValueError(f"Gagal membaca dataset: {e}")

        # Bersihkan data kosong
        self.dataset = self.dataset.dropna(subset=["Pertanyaan", "Jawaban"])
        self.questions = self.dataset["Pertanyaan"].astype(str).tolist()
        self.answers = self.dataset["Jawaban"].astype(str).tolist()

        # Preprocessing dan TF-IDF
        self.vectorizer = TfidfVectorizer()
        self.cleaned_questions = [self.preprocess(q) for q in self.questions]
        self.tfidf_matrix = self.vectorizer.fit_transform(self.cleaned_questions)
        print("✅ Vectorizer dan matrix TF-IDF berhasil dibuat")

    def preprocess(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def replace_synonyms(self, text: str) -> str:
        # Ganti tokenizer pakai split() biasa, bukan word_tokenize()
        words = text.split()

        new_words = []
        for word in words:
            synonyms = wordnet.synsets(word)
            if synonyms:
                lemma = synonyms[0].lemmas()[0].name().replace("_", " ")
                new_words.append(lemma)
            else:
                new_words.append(word)
        return ' '.join(new_words)

    def get_answer(self, query: str) -> tuple[str, int]:
        cleaned_query = self.replace_synonyms(self.preprocess(query))
        query_vec = self.vectorizer.transform([cleaned_query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        best_match_idx = similarities.argmax()
        best_score = similarities[best_match_idx]

        if best_score < 0.2:
            return "Maaf, saya tidak mengerti pertanyaan Anda.", -1
        return self.answers[best_match_idx], best_match_idx + 1


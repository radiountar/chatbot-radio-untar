from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.db import get_connection
import pandas as pd
import re

class LaguRetriever:
    def __init__(self):
        self.df = self._load_data()
        self.vectorizer = TfidfVectorizer()
        self.corpus = self.df["combined"].tolist()
        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)

    def _load_data(self):
        conn = get_connection()
        query = "SELECT id, judul, artist FROM lagu"
        df = pd.read_sql(query, conn)
        conn.close()

        # Gabungkan judul + artist dalam satu kolom teks
        df["combined"] = (df["judul"] + " " + df["artist"]).str.lower()
        return df

    def _preprocess(self, text):
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        return text.strip()

    def cari_lagu_terdekat(self, query, top_n=5):
        cleaned_query = self._preprocess(query)
        query_vec = self.vectorizer.transform([cleaned_query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = similarities.argsort()[::-1][:top_n]

        hasil = []
        for i in top_indices:
            score = round(similarities[i], 3)
            if score > 0.1:  # threshold
                row = self.df.iloc[i]
                hasil.append((row["judul"], row["artist"], score))
        return hasil

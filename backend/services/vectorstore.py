from __future__ import annotations
import os
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config import Config


class SimpleVectorStore:
    """基于 TF-IDF 的轻量向量存储，无需 GPU/模型下载，秒级启动。"""

    def __init__(self):
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        self._index_file = os.path.join(Config.DATA_DIR, "vec_index.json")
        self._chunks: list[dict] = []
        self._doc_ids: set[str] = set()
        self._dirty = False
        self._load()

    def _load(self):
        if os.path.exists(self._index_file):
            try:
                with open(self._index_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._chunks = data.get("chunks", [])
                self._doc_ids = set(data.get("doc_ids", []))
            except (json.JSONDecodeError, IOError):
                self._chunks = []
                self._doc_ids = set()

    def _save(self):
        with open(self._index_file, "w", encoding="utf-8") as f:
            json.dump({
                "chunks": self._chunks,
                "doc_ids": list(self._doc_ids),
            }, f, ensure_ascii=False)
        self._dirty = False

    def add_document(self, doc_id: str, chunks: list[dict]):
        for c in chunks:
            self._chunks.append({
                "content": c["content"],
                "doc_id": doc_id,
                "chunk_index": c["index"],
            })
        self._doc_ids.add(doc_id)
        self._dirty = True
        self._cache_clear()
        self._save()
        return len(chunks)

    def remove_document(self, doc_id: str):
        before = len(self._chunks)
        self._chunks = [c for c in self._chunks if c["doc_id"] != doc_id]
        self._doc_ids.discard(doc_id)
        if len(self._chunks) != before:
            self._dirty = True
            self._cache_clear()
            self._save()

    def _build_vectorizer(self) -> TfidfVectorizer:
        return TfidfVectorizer(
            analyzer="char_wb",
            max_features=5000,
            ngram_range=(2, 4),
            sublinear_tf=True,
        )

    def search(self, query: str, top_k: int = None) -> list[dict]:
        top_k = top_k or Config.TOP_K
        if not self._chunks:
            return []

        documents = [c["content"] for c in self._chunks]

        try:
            cached = getattr(self, '_cached_vec', None)
            cached_docs = getattr(self, '_cached_doc_count', 0)
            if cached is not None and cached_docs == len(documents):
                vec = self._cached_vec
                tfidf_matrix = self._cached_matrix
            else:
                vec = self._build_vectorizer()
                tfidf_matrix = vec.fit_transform(documents)
                self._cached_vec = vec
                self._cached_matrix = tfidf_matrix
                self._cached_doc_count = len(documents)
            query_vec = vec.transform([query])
            similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
        except Exception:
            # fallback: keyword matching
            query_lower = query.lower()
            similarities = np.array([
                sum(1 for w in query_lower.split() if w in c["content"].lower()) / max(len(c["content"].split()), 1)
                for c in self._chunks
            ])

        ranked = np.argsort(similarities)[::-1][:top_k]
        items = []
        for idx in ranked:
            score = float(similarities[idx])
            if score < 0.01:
                continue
            c = self._chunks[idx]
            items.append({
                "content": c["content"],
                "doc_id": c["doc_id"],
                "score": round(score, 4),
            })
        return items[:top_k]

    def get_document_count(self) -> dict[str, int]:
        return {d: 1 for d in self._doc_ids}

    def _cache_clear(self):
        self._cached_vec = None
        self._cached_matrix = None
        self._cached_doc_count = 0

    def clear(self):
        self._chunks = []
        self._doc_ids = set()
        self._dirty = True
        self._cache_clear()
        self._save()


vector_store = SimpleVectorStore()

from __future__ import annotations
import json
import os
import time
from config import Config


class FAQManager:
    def __init__(self):
        self._file = os.path.join(Config.DATA_DIR, "faq_pairs.json")
        os.makedirs(Config.DATA_DIR, exist_ok=True)

    def _load(self) -> list[dict]:
        if os.path.exists(self._file):
            with open(self._file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save(self, pairs: list[dict]):
        with open(self._file, "w", encoding="utf-8") as f:
            json.dump(pairs, f, ensure_ascii=False, indent=2)

    def list(self, keyword: str = "") -> list[dict]:
        pairs = self._load()
        if keyword:
            kw = keyword.lower()
            pairs = [
                p for p in pairs
                if kw in p["question"].lower() or kw in p["answer"].lower()
            ]
        return sorted(pairs, key=lambda p: p.get("updated_at", 0), reverse=True)

    def add(self, question: str, answer: str, category: str = "") -> dict:
        pairs = self._load()
        pair = {
            "id": str(int(time.time() * 1000)),
            "question": question.strip(),
            "answer": answer.strip(),
            "category": category.strip(),
            "created_at": int(time.time()),
            "updated_at": int(time.time()),
        }
        pairs.append(pair)
        self._save(pairs)
        return pair

    def update(self, pair_id: str, question: str, answer: str, category: str = "") -> dict:
        pairs = self._load()
        for p in pairs:
            if p["id"] == pair_id:
                p["question"] = question.strip()
                p["answer"] = answer.strip()
                p["category"] = category.strip()
                p["updated_at"] = int(time.time())
                self._save(pairs)
                return p
        raise ValueError(f"FAQ pair not found: {pair_id}")

    def delete(self, pair_id: str):
        pairs = self._load()
        pairs = [p for p in pairs if p["id"] != pair_id]
        self._save(pairs)

    def delete_batch(self, ids: list):
        id_set = set(ids)
        pairs = self._load()
        pairs = [p for p in pairs if p["id"] not in id_set]
        self._save(pairs)

    def search_faq(self, question: str) -> list[dict]:
        pairs = self._load()
        q_lower = question.lower()
        scored = []
        for p in pairs:
            score = 0
            p_q = p["question"].lower()
            if q_lower == p_q:
                score = 100
            elif q_lower in p_q or p_q in q_lower:
                score = 50
            else:
                q_words = set(q_lower.split())
                p_words = set(p_q.split())
                common = q_words & p_words
                if common:
                    score = len(common) / max(len(q_words), len(p_words)) * 30
            if score > 0:
                scored.append((score, p))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored[:5]]


faq_manager = FAQManager()

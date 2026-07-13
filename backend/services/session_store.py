from __future__ import annotations
import json
import os
import time
from config import Config


class SessionStore:
    """持久化会话存储，服务重启不丢失。"""

    def __init__(self):
        self._dir = os.path.join(Config.DATA_DIR, "sessions")
        os.makedirs(self._dir, exist_ok=True)

    def _path(self, sid: str) -> str:
        return os.path.join(self._dir, f"{sid}.json")

    def list_sessions(self) -> list[dict]:
        sessions = []
        for fname in os.listdir(self._dir):
            if not fname.endswith(".json"):
                continue
            filepath = os.path.join(self._dir, fname)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    s = json.load(f)
                sessions.append({
                    "id": s.get("id", ""),
                    "title": s.get("title", "未命名会话"),
                    "message_count": len(s.get("messages", [])),
                    "created_at": s.get("created_at", 0),
                    "updated_at": s.get("updated_at", 0),
                })
            except (json.JSONDecodeError, IOError):
                pass
        sessions.sort(key=lambda s: s["updated_at"], reverse=True)
        return sessions

    def get(self, sid: str) -> dict:
        filepath = self._path(sid)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "id": sid,
            "title": "未命名会话",
            "messages": [],
            "created_at": int(time.time()),
            "updated_at": int(time.time()),
        }

    def save(self, sid: str, messages: list[dict], title: str = None):
        s = self.get(sid)
        s["messages"] = messages
        s["updated_at"] = int(time.time())
        if title:
            s["title"] = title
        elif not s.get("title") or s["title"] == "未命名会话":
            for m in messages:
                if m["role"] == "user":
                    s["title"] = m["content"][:40]
                    break
        with open(self._path(sid), "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=2)

    def rename(self, sid: str, title: str):
        s = self.get(sid)
        s["title"] = title
        s["updated_at"] = int(time.time())
        with open(self._path(sid), "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=2)

    def delete(self, sid: str):
        filepath = self._path(sid)
        if os.path.exists(filepath):
            os.remove(filepath)

    def get_messages(self, sid: str) -> list[dict]:
        s = self.get(sid)
        return s.get("messages", [])


session_store = SessionStore()

from __future__ import annotations
import os
import json
import time
from flask import Blueprint, request, jsonify
from services.vectorstore import vector_store
from services.faq import faq_manager
from services.session_store import session_store
from config import Config

bp = Blueprint("stats", __name__, url_prefix="/api/stats")

FEEDBACK_FILE = os.path.join(Config.DATA_DIR, "feedback.json")


def _load_feedback() -> list[dict]:
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


@bp.route("/overview", methods=["GET"])
def overview():
    sessions = session_store.list_sessions()
    total_messages = sum(s["message_count"] for s in sessions)
    faq_pairs = faq_manager.list()
    docs = vector_store.get_document_count()
    feedback = _load_feedback()
    thumbs_up = sum(1 for f in feedback if f.get("type") == "up")
    thumbs_down = sum(1 for f in feedback if f.get("type") == "down")

    today_start = int(time.time()) - 86400
    today_sessions = [s for s in sessions if s["updated_at"] > today_start]

    return jsonify({"ok": True, "stats": {
        "total_sessions": len(sessions),
        "total_messages": total_messages,
        "faq_count": len(faq_pairs),
        "doc_count": len(docs),
        "thumbs_up": thumbs_up,
        "thumbs_down": thumbs_down,
        "today_sessions": len(today_sessions),
    }})


@bp.route("/feedback", methods=["POST"])
def save_feedback():
    data = request.get_json()
    if not data:
        return jsonify({"ok": False}), 400
    feedback = _load_feedback()
    feedback.append({
        "session_id": data.get("session_id", ""),
        "question": data.get("question", ""),
        "answer": data.get("answer", ""),
        "type": data.get("type", "up"),
        "timestamp": int(time.time()),
    })
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(feedback, f, ensure_ascii=False, indent=2)
    return jsonify({"ok": True})


@bp.route("/feedback", methods=["GET"])
def list_feedback():
    feedback = _load_feedback()
    limit = request.args.get("limit", 50, type=int)
    return jsonify({"ok": True, "items": feedback[-limit:][::-1]})

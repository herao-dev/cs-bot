from __future__ import annotations
import time
import uuid
from flask import Blueprint, request, jsonify
from services.rag import rag_service
from services.faq import faq_manager
from services.session_store import session_store
from config import Config

bp = Blueprint("chat", __name__, url_prefix="/api/chat")


@bp.route("/send", methods=["POST"])
def send_message():
    data = request.get_json()
    if not data or not data.get("question"):
        return jsonify({"ok": False, "message": "question is required"}), 400

    question = data["question"].strip()
    session_id = data.get("session_id", "")

    if not session_id:
        session_id = uuid.uuid4().hex[:12]

    messages = session_store.get_messages(session_id)
    recent = messages[-Config.MAX_HISTORY:]

    t0 = time.time()

    faq_matches = faq_manager.search_faq(question)
    if faq_matches:
        best = faq_matches[0]
        answer = best["answer"]
        sources = [{"doc_id": "faq", "score": 1.0, "excerpt": best["question"]}]
    else:
        result = rag_service.chat(question, recent)
        answer = result["answer"]
        sources = result["sources"]

    elapsed = round(time.time() - t0, 2)

    recent.append({"role": "user", "content": question})
    recent.append({"role": "assistant", "content": answer})
    session_store.save(session_id, recent[-Config.MAX_HISTORY:])

    return jsonify({
        "ok": True,
        "answer": answer,
        "sources": sources,
        "session_id": session_id,
        "elapsed": elapsed,
        "timestamp": int(time.time()),
    })


@bp.route("/history", methods=["GET"])
def get_history():
    session_id = request.args.get("session_id", "")
    if not session_id:
        return jsonify({"ok": False, "message": "session_id is required"}), 400
    messages = session_store.get_messages(session_id)
    return jsonify({"ok": True, "messages": messages})


@bp.route("/history", methods=["DELETE"])
def clear_history():
    session_id = request.args.get("session_id", "")
    if not session_id:
        return jsonify({"ok": False, "message": "session_id is required"}), 400
    session_store.save(session_id, [])
    return jsonify({"ok": True})


@bp.route("/sessions", methods=["GET"])
def list_sessions():
    sessions = session_store.list_sessions()
    return jsonify({"ok": True, "sessions": sessions})


@bp.route("/sessions", methods=["POST"])
def create_session():
    session_id = uuid.uuid4().hex[:12]
    session_store.save(session_id, [])
    return jsonify({"ok": True, "session_id": session_id})


@bp.route("/sessions/<session_id>", methods=["PUT"])
def rename_session(session_id):
    data = request.get_json()
    title = data.get("title", "").strip() if data else ""
    if title:
        session_store.rename(session_id, title)
    return jsonify({"ok": True})


@bp.route("/sessions/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    session_store.delete(session_id)
    return jsonify({"ok": True})

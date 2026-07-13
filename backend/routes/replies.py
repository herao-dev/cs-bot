from __future__ import annotations
import json
import os
import time
from flask import Blueprint, request, jsonify
from config import Config

bp = Blueprint("replies", __name__, url_prefix="/api/replies")

REPLIES_FILE = os.path.join(Config.DATA_DIR, "quick_replies.json")


def _load() -> list[dict]:
    if os.path.exists(REPLIES_FILE):
        try:
            with open(REPLIES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


def _save(items: list[dict]):
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    with open(REPLIES_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


@bp.route("", methods=["GET"])
def list_replies():
    items = _load()
    tag = request.args.get("tag", "")
    if tag:
        items = [r for r in items if r.get("tag") == tag]
    return jsonify({"ok": True, "items": sorted(items, key=lambda r: r.get("sort", 0))})


@bp.route("", methods=["POST"])
def add_reply():
    data = request.get_json()
    if not data or not data.get("title") or not data.get("content"):
        return jsonify({"ok": False, "message": "title and content are required"}), 400
    items = _load()
    item = {
        "id": str(int(time.time() * 1000)),
        "title": data["title"].strip(),
        "content": data["content"].strip(),
        "tag": data.get("tag", "").strip(),
        "sort": data.get("sort", len(items)),
        "created_at": int(time.time()),
    }
    items.append(item)
    _save(items)
    return jsonify({"ok": True, "item": item})


@bp.route("/<item_id>", methods=["PUT"])
def update_reply(item_id):
    data = request.get_json()
    if not data:
        return jsonify({"ok": False}), 400
    items = _load()
    for r in items:
        if r["id"] == item_id:
            if data.get("title"):
                r["title"] = data["title"].strip()
            if data.get("content"):
                r["content"] = data["content"].strip()
            if "tag" in data:
                r["tag"] = data.get("tag", "").strip()
            if "sort" in data:
                r["sort"] = data["sort"]
            _save(items)
            return jsonify({"ok": True, "item": r})
    return jsonify({"ok": False, "message": "Not found"}), 404


@bp.route("/<item_id>", methods=["DELETE"])
def delete_reply(item_id):
    items = _load()
    items = [r for r in items if r["id"] != item_id]
    _save(items)
    return jsonify({"ok": True})


@bp.route("/batch-delete", methods=["POST"])
def batch_delete():
    data = request.get_json()
    ids = set(data.get("ids", []) if data else [])
    items = _load()
    items = [r for r in items if r["id"] not in ids]
    _save(items)
    return jsonify({"ok": True})

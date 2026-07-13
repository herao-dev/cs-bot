import os
import uuid
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from config import Config
from services.document import parse_file, chunk_text
from services.vectorstore import vector_store
from services.faq import faq_manager

bp = Blueprint("knowledge", __name__, url_prefix="/api/knowledge")

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "md"}


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/documents", methods=["GET"])
def list_documents():
    docs = vector_store.get_document_count()
    return jsonify({"ok": True, "documents": [{"id": k, "name": k} for k in docs]})


@bp.route("/documents/upload", methods=["POST"])
def upload_document():
    file = request.files.get("file")
    if not file:
        return jsonify({"ok": False, "message": "No file provided"}), 400
    if not _allowed(file.filename):
        return jsonify({"ok": False, "message": f"Unsupported format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)

    original_name = secure_filename(file.filename or "unnamed")
    doc_id = f"{uuid.uuid4().hex[:10]}_{original_name}"
    filepath = os.path.join(Config.UPLOAD_DIR, doc_id)
    file.save(filepath)

    try:
        text = parse_file(filepath, original_name)
        chunks = chunk_text(text)
        if not chunks:
            return jsonify({"ok": False, "message": "Document is empty or could not be parsed"}), 400
        vector_store.add_document(doc_id, chunks)
        return jsonify({"ok": True, "document": {"id": doc_id, "name": original_name, "chunks": len(chunks)}})
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"ok": False, "message": str(e)}), 500


@bp.route("/documents/<doc_id>", methods=["DELETE"])
def delete_document(doc_id):
    vector_store.remove_document(doc_id)
    filepath = os.path.join(Config.UPLOAD_DIR, doc_id)
    if os.path.exists(filepath):
        os.remove(filepath)
    return jsonify({"ok": True})


@bp.route("/faq", methods=["GET"])
def list_faq():
    keyword = request.args.get("keyword", "")
    pairs = faq_manager.list(keyword)
    return jsonify({"ok": True, "pairs": pairs})


@bp.route("/faq", methods=["POST"])
def add_faq():
    data = request.get_json()
    if not data or not data.get("question") or not data.get("answer"):
        return jsonify({"ok": False, "message": "question and answer are required"}), 400
    pair = faq_manager.add(
        data["question"],
        data["answer"],
        data.get("category", ""),
    )
    return jsonify({"ok": True, "pair": pair})


@bp.route("/faq/<pair_id>", methods=["PUT"])
def update_faq(pair_id):
    data = request.get_json()
    if not data:
        return jsonify({"ok": False}), 400
    try:
        pair = faq_manager.update(
            pair_id,
            data.get("question", ""),
            data.get("answer", ""),
            data.get("category", ""),
        )
        return jsonify({"ok": True, "pair": pair})
    except ValueError as e:
        return jsonify({"ok": False, "message": str(e)}), 404


@bp.route("/faq/<pair_id>", methods=["DELETE"])
def delete_faq(pair_id):
    faq_manager.delete(pair_id)
    return jsonify({"ok": True})


@bp.route("/faq/batch-delete", methods=["POST"])
def batch_delete_faq():
    data = request.get_json()
    ids = data.get("ids", []) if data else []
    faq_manager.delete_batch(ids)
    return jsonify({"ok": True})

from flask import Flask
from flask_cors import CORS
from config import Config
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    os.makedirs(Config.DATA_DIR, exist_ok=True)
    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)

    from routes.knowledge import bp as knowledge_bp
    from routes.chat import bp as chat_bp
    from routes.stats import bp as stats_bp
    from routes.replies import bp as replies_bp

    app.register_blueprint(knowledge_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(replies_bp)

    @app.route("/api/health")
    def health():
        return {"ok": True, "service": "faq-bot"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5199, debug=True)

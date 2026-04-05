# app.py
import os
import threading
from flask import Flask, jsonify
from config import Config


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    app.json.ensure_ascii = False

    from routes.webhook import bp as webhook_bp
    app.register_blueprint(webhook_bp)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Rota não encontrada"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"erro": "Erro interno"}), 500

    return app


def start_telegram_bot():
    """Inicia o bot do Telegram em uma thread separada."""
    try:
        from telegram_bot import main
        main()
    except Exception as e:
        print(f"Erro no bot do Telegram: {e}")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app = create_app()

    # Inicia o bot do Telegram em background
    bot_thread = threading.Thread(target=start_telegram_bot, daemon=True)
    bot_thread.start()

    app.run(debug=False, host="0.0.0.0", port=port)
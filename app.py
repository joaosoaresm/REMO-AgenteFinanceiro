# app.py
# Entry point da aplicação. Usa factory pattern para
# facilitar testes e múltiplos ambientes.

from flask import Flask, jsonify
from config import Config


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # Blueprints
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


if __name__ == "__main__":
    app = create_app()
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=5000)

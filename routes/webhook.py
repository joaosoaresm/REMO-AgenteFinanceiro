# routes/webhook.py
# Ponto de integração com o n8n / WhatsApp.
# Recebe mensagem → interpreta → salva → responde.

from flask import Blueprint, request, jsonify
from services.message_interpreter import interpretar
from services.transaction_service import adicionar_transacao
from services.summary_service     import gerar_resumo
from services.tips_service        import gerar_dicas

bp = Blueprint("webhook", __name__, url_prefix="/webhook")


@bp.post("/mensagem")
def receber_mensagem():
    """
    POST /webhook/mensagem
    Body: { "mensagem": "gastei 20 no lanche" }

    Fluxo:
      1. Valida entrada
      2. Detecta comando especial (resumo / dicas)
      3. Interpreta como transação
      4. Salva e retorna confirmação
    """
    payload  = request.get_json(silent=True) or {}
    mensagem = payload.get("mensagem", "").strip()

    if not mensagem:
        return jsonify({"erro": "Campo 'mensagem' é obrigatório."}), 400

    # Comandos especiais
    resposta = _verificar_comando(mensagem)
    if resposta:
        return jsonify({"resposta": resposta})

    # Interpreta como transação financeira
    resultado = interpretar(mensagem)
    if not resultado:
        return jsonify({
            "resposta": (
                "Não entendi. Tente:\n"
                "• 'gastei 50 no mercado'\n"
                "• 'recebi 1000 de salário'\n"
                "• 'resumo' para ver seu extrato\n"
                "• 'dicas' para dicas financeiras"
            )
        })

    try:
        transacao = adicionar_transacao(
            tipo      = resultado["tipo"],
            valor     = resultado["valor"],
            descricao = resultado["descricao"],
        )
        return jsonify({
            "resposta":  _formatar_confirmacao(transacao),
            "transacao": transacao,
        })
    except ValueError as e:
        return jsonify({"erro": str(e)}), 422


# ── helpers privados ──────────────────────────────────────────────────────────

_COMANDOS_RESUMO = {"resumo", "extrato", "saldo", "quanto tenho"}
_COMANDOS_DICAS  = {"dicas", "dica", "conselho", "me ajuda"}


def _verificar_comando(mensagem: str) -> str | None:
    """Detecta se a mensagem é um comando especial."""
    msg = mensagem.lower().strip()
    if msg in _COMANDOS_RESUMO:
        return gerar_resumo()
    if msg in _COMANDOS_DICAS:
        return gerar_dicas()
    return None


def _formatar_confirmacao(transacao: dict) -> str:
    emoji = "💸" if transacao["tipo"] == "gasto" else "💰"
    tipo  = transacao["tipo"].capitalize()
    return (
        f"{emoji} Registrado!\n"
        f"Tipo: {tipo}\n"
        f"Valor: R$ {transacao['valor']:.2f}\n"
        f"Descrição: {transacao['descricao'].capitalize()}\n"
        f"Categoria: {transacao.get('categoria', 'outros').capitalize()}"
    )
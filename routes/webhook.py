# routes/webhook.py
from flask import Blueprint, request, jsonify
from services.message_interpreter import interpretar
from services.transaction_service import adicionar_transacao, calcular_saldo, deletar_transacao
from services.summary_service     import gerar_resumo
from services.tips_service        import gerar_dicas
from services.gemini_service      import perguntar_ia, analisar_financas

bp = Blueprint("webhook", __name__, url_prefix="/webhook")


@bp.post("/mensagem")
def receber_mensagem():
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
        # Não entendeu como transação — pergunta para o Gemini
        resposta_ia = perguntar_ia(mensagem)
        return jsonify({"resposta": resposta_ia})

    try:
        transacao = adicionar_transacao(
            tipo      = resultado["tipo"],
            valor     = resultado["valor"],
            descricao = resultado["descricao"],
            categoria = resultado.get("categoria"),
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
_COMANDOS_IA     = {"analisar", "análise", "analisa", "o que acha"}
_COMANDOS_RESET = {"zerar", "resetar", "novo mês", "novo mes", "limpar"}

# Atualiza a função _verificar_comando
def _verificar_comando(mensagem: str) -> str | None:
    msg = mensagem.lower().strip()

    if msg in _COMANDOS_RESUMO:
        return gerar_resumo()

    if msg in _COMANDOS_DICAS:
        return gerar_dicas()

    if msg in _COMANDOS_IA:
        resumo = calcular_saldo()
        return analisar_financas(resumo)

    if msg in _COMANDOS_RESET:
        from services.transaction_service import zerar_transacoes
        zerar_transacoes()
        return "✅ Transações zeradas! Começando o novo mês do zero."

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

from services.transaction_service import (
    adicionar_transacao, calcular_saldo, listar_transacoes, deletar_transacao, zerar_transacoes
)

@bp.delete("/deletar/<string:transaction_id>")
def deletar_transacao_route(transaction_id: str):
    """DELETE /api/transacoes/<id>"""
    removido = deletar_transacao(transaction_id)
    if not removido:
        return jsonify({"erro": "Transação não encontrada"}), 404
    return jsonify({"mensagem": "Transação removida com sucesso!"})
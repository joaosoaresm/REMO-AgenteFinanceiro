# services/summary_service.py
# Gera resumos financeiros formatados para WhatsApp.

from collections import defaultdict
from services.transaction_service import listar_transacoes, calcular_saldo


def gerar_resumo() -> str:
    """
    Retorna um resumo financeiro completo formatado
    para envio via WhatsApp pelo n8n.
    """
    saldo     = calcular_saldo()
    transacoes = listar_transacoes()

    if not transacoes:
        return "Nenhuma transação registrada ainda."

    por_categoria = _agrupar_por_categoria(transacoes)
    linhas        = _formatar_categorias(por_categoria)
    rodape        = _formatar_rodape(saldo)

    return "\n".join([
        "📊 *Resumo Financeiro*",
        "─────────────────────",
        *linhas,
        "─────────────────────",
        *rodape,
    ])


# ── helpers privados ──────────────────────────────────────────────────────────

def _agrupar_por_categoria(transacoes: list[dict]) -> dict:
    """Soma os gastos por categoria (ignora ganhos no agrupamento)."""
    grupos = defaultdict(float)
    for t in transacoes:
        if t["tipo"] == "gasto":
            grupos[t.get("categoria", "outros")] += t["valor"]
    return dict(sorted(grupos.items(), key=lambda x: x[1], reverse=True))


def _formatar_categorias(por_categoria: dict) -> list[str]:
    if not por_categoria:
        return ["Nenhum gasto registrado."]
    return [
        f"  {_emoji_categoria(cat)} {cat.capitalize()}: R$ {total:.2f}"
        for cat, total in por_categoria.items()
    ]


def _formatar_rodape(saldo: dict) -> list[str]:
    sinal  = "+" if saldo["saldo"] >= 0 else ""
    emoji  = "✅" if saldo["saldo"] >= 0 else "⚠️"
    return [
        f"💰 Ganhos:  R$ {saldo['ganhos']:.2f}",
        f"💸 Gastos:  R$ {saldo['gastos']:.2f}",
        f"{emoji} Saldo:   {sinal}R$ {saldo['saldo']:.2f}",
    ]


def _emoji_categoria(categoria: str) -> str:
    emojis = {
        "alimentação": "🍔",
        "transporte":  "🚗",
        "saúde":       "💊",
        "lazer":       "🎬",
        "moradia":     "🏠",
        "renda":       "💼",
        "outros":      "📦",
    }
    return emojis.get(categoria, "📦")
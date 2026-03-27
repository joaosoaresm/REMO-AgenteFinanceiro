# services/tips_service.py
# Analisa o histórico e gera dicas financeiras personalizadas.

from collections import defaultdict
from services.transaction_service import listar_transacoes, calcular_saldo

# Percentual de gasto em uma categoria que dispara uma dica
_LIMITE_PERCENTUAL = 0.30  # 30% do total gasto


def gerar_dicas() -> str:
    """
    Analisa as transações e retorna dicas formatadas para WhatsApp.
    """
    transacoes = listar_transacoes()

    if not transacoes:
        return "Ainda não há transações para analisar. Comece registrando seus gastos!"

    saldo          = calcular_saldo()
    por_categoria  = _somar_por_categoria(transacoes)
    dicas          = _analisar(por_categoria, saldo)

    if not dicas:
        return "✅ Seus gastos estão equilibrados. Continue assim!"

    linhas = ["💡 *Dicas Financeiras*", "─────────────────────"]
    linhas += [f"  {i+1}. {dica}" for i, dica in enumerate(dicas)]
    return "\n".join(linhas)


# ── helpers privados ──────────────────────────────────────────────────────────

def _somar_por_categoria(transacoes: list[dict]) -> dict:
    totais = defaultdict(float)
    for t in transacoes:
        if t["tipo"] == "gasto":
            totais[t.get("categoria", "outros")] += t["valor"]
    return dict(totais)


def _analisar(por_categoria: dict, saldo: dict) -> list[str]:
    """Aplica as regras de análise e retorna lista de dicas."""
    dicas = []
    total_gastos = saldo["gastos"]

    if total_gastos == 0:
        return dicas

    for categoria, total in por_categoria.items():
        percentual = total / total_gastos

        if percentual >= _LIMITE_PERCENTUAL:
            dicas.append(_dica_categoria_alta(categoria, total, percentual))

    if saldo["saldo"] < 0:
        dicas.append(
            f"Seu saldo está negativo (R$ {saldo['saldo']:.2f}). "
            "Evite novos gastos até equilibrar."
        )
    elif saldo["saldo"] < saldo["ganhos"] * 0.10:
        dicas.append(
            "Você está economizando menos de 10% da sua renda. "
            "Tente guardar pelo menos 10% todo mês."
        )

    return dicas


def _dica_categoria_alta(categoria: str, total: float, percentual: float) -> str:
    reducao = total * 0.20
    return (
        f"Você gastou {percentual:.0%} do seu orçamento em "
        f"{categoria} (R$ {total:.2f}). "
        f"Reduzir 20% economizaria R$ {reducao:.2f} por mês."
    )   
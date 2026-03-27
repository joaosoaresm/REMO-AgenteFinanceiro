# services/transaction_service.py
# Lógica de negócio para transações financeiras.
# Ponto central para criar, listar e resumir transações.

from datetime import date
from config import Config
from utils import json_storage as db


# ── escrita ───────────────────────────────────────────────────────────────────

def adicionar_transacao(tipo: str, valor: float, descricao: str) -> dict:
    """
    Cria e persiste uma nova transação.
    Raises ValueError se tipo for inválido ou valor <= 0.
    """
    _validar(tipo, valor)

    transacao = {
        "tipo":      tipo,
        "valor":     valor,
        "descricao": descricao.strip(),
        "categoria": _inferir_categoria(descricao),
        "data":      date.today().isoformat(),
    }
    return db.insert(Config.TRANSACTIONS_FILE, transacao)


# ── leitura ───────────────────────────────────────────────────────────────────

def listar_transacoes(tipo: str = None) -> list[dict]:
    """
    Lista todas as transações.
    Filtra por tipo ("gasto" | "ganho") se informado.
    """
    registros = db.load_all(Config.TRANSACTIONS_FILE)
    if tipo:
        registros = [r for r in registros if r.get("tipo") == tipo]
    return sorted(registros, key=lambda r: r["created_at"], reverse=True)


def calcular_saldo() -> dict:
    """
    Retorna total de ganhos, gastos e saldo líquido.
    """
    registros = db.load_all(Config.TRANSACTIONS_FILE)
    ganhos = sum(r["valor"] for r in registros if r["tipo"] == "ganho")
    gastos = sum(r["valor"] for r in registros if r["tipo"] == "gasto")
    return {
        "ganhos": round(ganhos, 2),
        "gastos": round(gastos, 2),
        "saldo":  round(ganhos - gastos, 2),
    }


# ── helpers privados ──────────────────────────────────────────────────────────

def _validar(tipo: str, valor: float) -> None:
    if tipo not in ("gasto", "ganho"):
        raise ValueError(f"Tipo inválido: '{tipo}'. Use 'gasto' ou 'ganho'.")
    if not isinstance(valor, (int, float)) or valor <= 0:
        raise ValueError(f"Valor inválido: {valor}. Deve ser maior que zero.")


# Mapa simples de palavras → categoria
_CATEGORIAS: dict[str, list[str]] = {
    "alimentação":  ["lanche", "comida", "mercado", "restaurante",
                     "delivery", "almoço", "jantar", "café"],
    "transporte":   ["uber", "ônibus", "gasolina", "combustível",
                     "táxi", "metro", "estacionamento"],
    "saúde":        ["remédio", "farmácia", "médico", "consulta",
                     "hospital", "plano"],
    "lazer":        ["cinema", "netflix", "spotify", "jogo",
                     "viagem", "show", "bar"],
    "moradia":      ["aluguel", "luz", "água", "internet",
                     "condomínio", "gás"],
    "renda":        ["salário", "freela", "freelance", "venda",
                     "cliente", "projeto"],
}


def _inferir_categoria(descricao: str) -> str:
    desc = descricao.lower()
    for categoria, palavras in _CATEGORIAS.items():
        if any(p in desc for p in palavras):
            return categoria
    return "outros"
# services/message_interpreter.py
# Interpreta mensagens em linguagem natural e extrai
# tipo, valor e descrição usando regex — sem IA externa.

import re

# Palavras que indicam GASTO
_GASTO_KEYWORDS = (
    r"gast(ei|ou)|pagu(ei|ou)|comprei|saiu|saída|"
    r"debit(ei|ou)|tirei|perdi"
)

# Palavras que indicam GANHO
_GANHO_KEYWORDS = (
    r"ganhei|recebi|entrou|renda|salário|freela|"
    r"vendi|lucrei|depósito"
)

# Padrão para capturar valores monetários
# Aceita: 20 / 20.50 / 20,50 / R$20 / R$ 20,50
_VALOR_PATTERN = r"R?\$?\s*(\d{1,6}(?:[.,]\d{1,2})?)"

# Palavras de ligação a ignorar na descrição
_PREPOSICOES = re.compile(
    r"\b(no|na|com|de|do|da|em|pro|pra|num|uma?)\b", re.I
)


def interpretar(mensagem: str) -> dict | None:
    """
    Tenta extrair tipo, valor e descrição de uma frase.
    Retorna None se não conseguir interpretar.

    Exemplos aceitos:
        "gastei 20 no lanche"        → gasto, 20.0,  "lanche"
        "ganhei 500 freelando"       → ganho, 500.0, "freelando"
        "paguei R$150,00 no mercado" → gasto, 150.0, "mercado"
        "recebi 1200 de salário"     → ganho, 1200.0,"salário"
    """
    msg = mensagem.strip().lower()

    tipo = _detectar_tipo(msg)
    if not tipo:
        return None

    valor = _extrair_valor(msg)
    if not valor:
        return None

    descricao = _extrair_descricao(msg, valor)

    return {
        "tipo":      tipo,
        "valor":     valor,
        "descricao": descricao,
    }


# ── helpers privados ──────────────────────────────────────────────────────────

def _detectar_tipo(msg: str) -> str | None:
    if re.search(_GASTO_KEYWORDS, msg, re.I):
        return "gasto"
    if re.search(_GANHO_KEYWORDS, msg, re.I):
        return "ganho"
    return None


def _extrair_valor(msg: str) -> float | None:
    match = re.search(_VALOR_PATTERN, msg, re.I)
    if not match:
        return None
    raw = match.group(1).replace(",", ".")
    try:
        return round(float(raw), 2)
    except ValueError:
        return None


def _extrair_descricao(msg: str, valor: float) -> str:
    """
    Remove palavras-chave de tipo, o valor e preposições,
    deixando apenas a descrição limpa.
    """
    texto = msg

    # Remove o valor monetário (ex: 50, 50.00, R$50)
    texto = re.sub(r"R?\$?\s*\d+(?:[.,]\d{1,2})?", "", texto, flags=re.I)

    # Remove palavras de tipo
    texto = re.sub(_GASTO_KEYWORDS, "", texto, flags=re.I)
    texto = re.sub(_GANHO_KEYWORDS, "", texto, flags=re.I)

    # Remove preposições e artigos soltos
    texto = _PREPOSICOES.sub("", texto)

    # Limpa espaços extras e pontuação solta
    texto = re.sub(r"[^\w\s]", "", texto)
    descricao = " ".join(texto.split()).strip()

    return descricao if descricao else "sem descrição"
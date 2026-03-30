# services/gemini_service.py
# Integração com a API do Gemini (Google).
# Envia contexto financeiro e retorna resposta inteligente.

import requests
from config import Config

# URL da API Gemini
_GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent?key={key}"
)

# Personalidade do REMO
_SYSTEM_PROMPT = """
Você é o REMO (Real Money), um assistente financeiro pessoal inteligente.
Seu papel é ajudar o usuário a controlar suas finanças pessoais.

Regras:
- Responda sempre em português brasileiro
- Seja direto e objetivo
- Use linguagem simples e amigável
- Quando houver dados financeiros, analise e dê insights úteis
- Sugira economia quando identificar gastos altos
- Máximo de 3 parágrafos por resposta
"""


def perguntar_ia(mensagem: str, contexto: str = "") -> str:
    """
    Envia mensagem para o Gemini e retorna resposta da IA.

    Args:
        mensagem: Pergunta ou texto do usuário
        contexto: Dados financeiros para enriquecer a resposta (opcional)

    Returns:
        Resposta da IA como string.
    """
    if not Config.GEMINI_API_KEY:
        return "Chave da API Gemini não configurada."

    prompt = _montar_prompt(mensagem, contexto)

    try:
        return _chamar_api(prompt)
    except requests.exceptions.Timeout:
        return "A IA demorou para responder. Tente novamente."
    except requests.exceptions.ConnectionError:
        return "Sem conexão com a IA no momento. Tente novamente."
    except Exception as e:
        return f"Erro ao consultar IA: {str(e)}"


def analisar_financas(resumo: dict) -> str:
    """
    Recebe um resumo financeiro e pede análise para o Gemini.

    Args:
        resumo: Dicionário com ganhos, gastos e saldo

    Returns:
        Análise e dicas da IA
    """
    contexto = (
        f"Dados financeiros do usuário:\n"
        f"- Ganhos: R$ {resumo.get('ganhos', 0):.2f}\n"
        f"- Gastos: R$ {resumo.get('gastos', 0):.2f}\n"
        f"- Saldo:  R$ {resumo.get('saldo', 0):.2f}"
    )
    return perguntar_ia(
        "Analise minha situação financeira e me dê dicas práticas.", contexto
    )


# ── helpers privados ──────────────────────────────────────────────────────────

def _montar_prompt(mensagem: str, contexto: str) -> str:
    """Monta o prompt completo com contexto financeiro."""
    if contexto:
        return f"{_SYSTEM_PROMPT}\n\n{contexto}\n\nPergunta: {mensagem}"
    return f"{_SYSTEM_PROMPT}\n\nPergunta: {mensagem}"


def _chamar_api(prompt: str) -> str:
    """Faz a chamada HTTP para a API do Gemini."""
    url = _GEMINI_URL.format(
        model=Config.GEMINI_MODEL,
        key=Config.GEMINI_API_KEY,
    )

    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature":     0.7,
            "maxOutputTokens": 500,
        }
    }

    response = requests.post(url, json=body, timeout=15)
    response.raise_for_status()

    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
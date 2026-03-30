# services/groq_service.py
# Integração com a API da Groq.
# Envia contexto financeiro e retorna resposta inteligente da IA.

import requests
from config import Config

# URL oficial da API Groq
_GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Personalidade e contexto do REMO
_SYSTEM_PROMPT = """
Você é o REMO, um assistente financeiro pessoal inteligente e direto.
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
    Envia mensagem para o Groq e retorna resposta da IA.

    Args:
        mensagem: Pergunta ou texto do usuário
        contexto: Dados financeiros para enriquecer a resposta (opcional)

    Returns:
        Resposta da IA como string. Em caso de erro, retorna mensagem padrão.
    """
    if not Config.GROQ_API_KEY:
        return "Chave da API Groq não configurada."

    prompt = _montar_prompt(mensagem, contexto)

    try:
        resposta = _chamar_api(prompt)
        return resposta
    except requests.exceptions.Timeout:
        return "A IA demorou para responder. Tente novamente."
    except requests.exceptions.ConnectionError:
        return "Sem conexão com a IA no momento. Tente novamente."
    except Exception as e:
        return f"Erro ao consultar IA: {str(e)}"


def analisar_financas(resumo: dict) -> str:
    """
    Recebe um resumo financeiro e pede análise para a IA.

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
    return perguntar_ia("Analise minha situação financeira e me dê dicas.", contexto)


# ── helpers privados ──────────────────────────────────────────────────────────

def _montar_prompt(mensagem: str, contexto: str) -> str:
    """Monta o prompt completo com contexto financeiro."""
    if contexto:
        return f"{contexto}\n\nPergunta do usuário: {mensagem}"
    return mensagem


def _chamar_api(prompt: str) -> str:
    """Faz a chamada HTTP para a API do Groq."""
    headers = {
        "Authorization": f"Bearer {Config.GROQ_API_KEY}",
        "Content-Type":  "application/json",
    }

    body = {
        "model": Config.GROQ_MODEL,
        "messages": [
            {"role": "system",  "content": _SYSTEM_PROMPT},
            {"role": "user",    "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens":  500,
    }

    response = requests.post(
        _GROQ_URL,
        headers=headers,
        json=body,
        timeout=15,
    )
    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()
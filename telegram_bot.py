# telegram_bot.py
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
API_URL        = os.getenv("API_URL", "https://remo-financial.onrender.com/webhook/mensagem")
TELEGRAM_API   = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Usuários autorizados — adiciona o chat_id aqui
USUARIOS_AUTORIZADOS = {6075543761}


def get_updates(offset: int = None) -> list:
    params = {"timeout": 30, "offset": offset}
    try:
        response = requests.get(
            f"{TELEGRAM_API}/getUpdates",
            params=params,
            timeout=35
        )
        return response.json().get("result", [])
    except Exception:
        return []


def send_message(chat_id: int, text: str) -> None:
    try:
        requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={
                "chat_id":    chat_id,
                "text":       text,
                "parse_mode": "Markdown"
            },
            timeout=10
        )
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")


def processar_mensagem(mensagem: str) -> str:
    try:
        response = requests.post(
            API_URL,
            json={"mensagem": mensagem},
            timeout=15
        )
        data = response.json()
        return data.get("resposta") or data.get("erro", "Erro desconhecido")
    except Exception as e:
        return f"Erro ao conectar com o REMO: {str(e)}"


def main():
    print("🤖 REMO Bot iniciado!")
    offset = None

    while True:
        updates = get_updates(offset)

        for update in updates:
            offset = update["update_id"] + 1

            if "message" not in update:
                continue

            chat_id = update["message"]["chat"]["id"]
            nome    = update["message"]["chat"].get("first_name", "")
            texto   = update["message"].get("text", "").strip()

            if not texto:
                continue

            print(f"📩 {nome} ({chat_id}): {texto}")

            # Bloqueia usuários não autorizados
            if chat_id not in USUARIOS_AUTORIZADOS:
                send_message(chat_id,
                    "⛔ Acesso não autorizado.\n"
                    "Este bot é privado."
                )
                continue

            # Comando /start
            if texto == "/start":
                resposta = (
                    f"Olá, {nome}! 👋\n"
                    f"Eu sou o *REMO*, seu assistente financeiro pessoal.\n\n"
                    f"Você pode me dizer:\n"
                    f"• 'gastei 50 no mercado'\n"
                    f"• 'recebi 1500 de salário'\n"
                    f"• 'resumo' para ver seu extrato\n"
                    f"• 'dicas' para dicas financeiras\n"
                    f"• 'zerar' para resetar no novo mês"
                )
            else:
                resposta = processar_mensagem(texto)

            send_message(chat_id, resposta)
            print(f"✅ Respondido: {resposta[:50]}...")

        time.sleep(1)


if __name__ == "__main__":
    main()
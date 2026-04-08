# telegram_bot.py
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
API_URL        = os.getenv("API_URL", "https://remo-agentefinanceiro.onrender.com/webhook/mensagem")
DELETE_URL = "https://remo-agentefinanceiro.onrender.com/webhook/deletar"
TELEGRAM_API   = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

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


def send_message(chat_id: int, text: str, reply_markup: dict = None) -> None:
    """Envia mensagem com botão opcional."""
    body = {
        "chat_id":    chat_id,
        "text":       text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        body["reply_markup"] = reply_markup

    try:
        requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json=body,
            timeout=10
        )
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")


def delete_message(chat_id: int, message_id: int) -> None:
    """Remove uma mensagem do chat."""
    try:
        requests.post(
            f"{TELEGRAM_API}/deleteMessage",
            json={"chat_id": chat_id, "message_id": message_id},
            timeout=10
        )
    except Exception:
        pass


def answer_callback(callback_id: str, text: str = "") -> None:
    """Responde ao callback do botão."""
    try:
        requests.post(
            f"{TELEGRAM_API}/answerCallbackQuery",
            json={"callback_query_id": callback_id, "text": text},
            timeout=10
        )
    except Exception:
        pass


def edit_message(chat_id: int, message_id: int, text: str) -> None:
    """Edita uma mensagem existente."""
    try:
        requests.post(
            f"{TELEGRAM_API}/editMessageText",
            json={
                "chat_id":    chat_id,
                "message_id": message_id,
                "text":       text,
                "parse_mode": "Markdown"
            },
            timeout=10
        )
    except Exception:
        pass


def processar_mensagem(mensagem: str) -> dict:
    """Envia mensagem para a API do REMO e retorna resposta completa."""
    try:
        response = requests.post(
            API_URL,
            json={"mensagem": mensagem},
            timeout=15
        )
        return response.json()
    except Exception as e:
        return {"resposta": f"Erro ao conectar com o REMO: {str(e)}"}


def excluir_transacao(transaction_id: str) -> bool:
    """Exclui uma transação pelo ID."""
    try:
        response = requests.delete(
            f"{DELETE_URL}/{transaction_id}",
            timeout=10
        )
        return response.status_code == 200
    except Exception:
        return False


def botao_excluir(transaction_id: str) -> dict:
    """Cria o teclado inline com botão de excluir."""
    return {
        "inline_keyboard": [[
            {
                "text":          "❌ Excluir esta transação",
                "callback_data": f"delete_{transaction_id}"
            }
        ]]
    }


def main():
    print("🤖 REMO Bot iniciado!")
    offset = None

    while True:
        updates = get_updates(offset)

        for update in updates:
            offset = update["update_id"] + 1

            # Trata clique no botão de excluir
            if "callback_query" in update:
                callback  = update["callback_query"]
                chat_id   = callback["message"]["chat"]["id"]
                msg_id    = callback["message"]["message_id"]
                data      = callback.get("data", "")
                callback_id = callback["id"]

                if data.startswith("delete_"):
                    transaction_id = data.replace("delete_", "")
                    sucesso = excluir_transacao(transaction_id)

                    if sucesso:
                        answer_callback(callback_id, "✅ Transação excluída!")
                        edit_message(chat_id, msg_id, "~~Transação excluída~~✅")
                    else:
                        answer_callback(callback_id, "❌ Erro ao excluir!")
                continue

            # Trata mensagens normais
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
                send_message(chat_id, resposta)
                continue

            # Processa mensagem
            resultado  = processar_mensagem(texto)
            resposta   = resultado.get("resposta") or resultado.get("erro", "Erro desconhecido")
            transacao  = resultado.get("transacao")

            # Se registrou transação, adiciona botão de excluir
            if transacao and transacao.get("id"):
                send_message(chat_id, resposta, botao_excluir(transacao["id"]))
            else:
                send_message(chat_id, resposta)

            print(f"✅ Respondido: {resposta[:50]}...")

        time.sleep(1)


if __name__ == "__main__":
    main()
import logging
import sqlite3
import datetime
import os
import sys
from pathlib import Path
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# --- RESOLUÇÃO DE CAMINHO ---
# Garante que o Python encontre o pacote agent_core
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent_core.agent import build_agent
from agent_core.tools import escalate_to_human

# 1. Configuração de Logs
logging.basicConfig(level=logging.INFO, format="%(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("LojaIA")

# 2. Configuração de Persistência com SQLite
DB_PATH = Path("chat_history.db")

def init_database():
    """Inicializa o banco de dados SQLite para persistência de histórico"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL
            )
        """)
        conn.commit()

def save_to_history(session_id: str, user_message: str, ai_response: str):
    """Salva uma troca de mensagens no histórico"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO chat_history (session_id, user_message, ai_response) VALUES (?, ?, ?)",
            (session_id, user_message, ai_response)
        )
        conn.commit()

def load_history(session_id: str, limit: int = 10):
    """Carrega o histórico recente de uma sessão"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            """SELECT user_message, ai_response FROM chat_history
               WHERE session_id = ?
               ORDER BY id DESC
               LIMIT ?""",
            (session_id, limit)
        )
        return cursor.fetchall()

def _format_ai_response(content):
    """
    Trata a resposta do Gemini para garantir que apenas o texto puro seja exibido.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [block.get("text", "") for block in content if isinstance(block, dict) and "text" in block]
        if not parts:
            parts = [block.text for block in content if hasattr(block, "text")]
        return "\n".join(parts)
    return str(content)

def main():
    print("\n" + "="*40)
    print("🤖 Assistente Virtual da Loja (Lia)")
    print("Módulo: Terminal (Modo de Teste)")
    print("Digite 'sair' para encerrar.")
    print("="*40 + "\n")

    init_database()
    session_id = "terminal-user"
    agent = build_agent()

    # Carrega histórico recente
    chat_history = []
    recent_messages = load_history(session_id, limit=5)
    for user_msg, ai_msg in reversed(recent_messages):
        chat_history.append(HumanMessage(content=user_msg))
        chat_history.append(AIMessage(content=ai_msg))

    available_tools = {"escalate_to_human": escalate_to_human}

    while True:
        try:
            user_input = input("Você: ").strip()
            if user_input.lower() in ("sair", "exit", "quit"):
                print("\nLia: Até logo! Espero ter ajudado. 👋")
                break
            
            if not user_input:
                continue

            chat_history.append(HumanMessage(content=user_input))

            # Chamada ao agente
            response = agent.invoke({"messages": chat_history})

            # Lógica de Tool Calling
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"].lower()
                    if tool_name in available_tools:
                        tool_result = available_tools[tool_name].invoke(tool_call["args"])
                        
                        chat_history.append(response)
                        chat_history.append(ToolMessage(
                            tool_call_id=tool_call["id"],
                            content=str(tool_result)
                        ))
                        # Resposta final após a ferramenta
                        response = agent.invoke({"messages": chat_history})

            final_text = _format_ai_response(response.content)
            print(f"\nLia: {final_text}\n")

            chat_history.append(AIMessage(content=final_text))
            save_to_history(session_id, user_input, final_text)

        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Erro: {e}")
            print("\nLia: Tive um pequeno problema técnico, mas já estou me recuperando!")

if __name__ == "__main__":
    main()
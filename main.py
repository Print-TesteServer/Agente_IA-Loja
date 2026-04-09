import logging
import sqlite3
import datetime
from pathlib import Path
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from agent import build_agent
from tools import escalate_to_human

# 1. Configuração de Logs
# Definimos o nível WARNING para httpx para esconder as requisições POST do Google
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
               ORDER BY timestamp DESC
               LIMIT ?""",
            (session_id, limit)
        )
        return cursor.fetchall()

def _format_ai_response(content):
    """
    Trata a resposta do Gemini para garantir que apenas o texto puro seja exibido,
    removendo metadados ou estruturas de lista de blocos.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        # Filtra apenas a parte de texto dos blocos retornados
        parts = [block.get("text", "") for block in content if isinstance(block, dict) and "text" in block]
        # Caso os blocos sejam objetos do LangChain com atributo .text
        if not parts:
            parts = [block.text for block in content if hasattr(block, "text")]
        return "\n".join(parts)
    return str(content)

def main():
    print("=== Assistente Virtual da Loja (Lia) ===")
    print("Digite 'sair' para encerrar.\n")

    # Inicializa o banco de dados
    init_database()

    # Gera um ID de sessão FIXO para testes de memória
    # Em produção, seria baseado na data/hora atual ou dispositivo
    session_id = "test-user"

    # Inicializa o agente configurado no agent.py
    agent = build_agent()

    # Carrega histórico recente da sessão atual (se houver)
    chat_history = []
    recent_messages = load_history(session_id, limit=5)
    for user_msg, ai_msg in reversed(recent_messages):  # Reverse para ordem cronológica
        chat_history.append(HumanMessage(content=user_msg))
        chat_history.append(AIMessage(content=ai_msg))

    # Mapeamento de ferramentas disponíveis para execução manual pelo código
    available_tools = {"escalate_to_human": escalate_to_human}

    while True:
        try:
            user_input = input("Você: ").strip()
            if user_input.lower() in ("sair", "exit", "quit"):
                print("Até mais!")
                break
            if not user_input:
                continue

            # Adiciona a interação do usuário ao histórico de contexto
            chat_history.append(HumanMessage(content=user_input))

            # Primeira chamada ao agente
            response = agent.invoke({"messages": chat_history})

            # Verificação de Tool Calling (Execução de Automação)
            if response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"].lower()
                    tool_args = tool_call["args"]

                    if tool_name in available_tools:
                        # Executa a ferramenta (dispara o print do Webhook no console)
                        tool_func = available_tools[tool_name]
                        tool_result = tool_func.invoke(tool_args)

                        # Registra a intenção da IA e o resultado da ferramenta no histórico
                        chat_history.append(response)
                        chat_history.append(ToolMessage(
                            tool_call_id=tool_call["id"],
                            content=str(tool_result)
                        ))

                        # Nova chamada ao agente para que ele gere a resposta final baseada no sucesso da tool
                        response = agent.invoke({"messages": chat_history})

            # Formata e exibe a resposta final limpa para o usuário
            final_text = _format_ai_response(response.content)
            print(f"\nAssistente: {final_text}\n")

            # Mantém a resposta final no histórico para continuidade da conversa
            chat_history.append(AIMessage(content=final_text))

            # Salva a troca no banco de dados persistente
            save_to_history(session_id, user_input, final_text)

        except Exception as e:
            logger.error(f"Ocorreu um erro inesperado: {e}")
            print("\nAssistente: Desculpe, tive um problema técnico. Podemos tentar novamente?\n")

if __name__ == "__main__":
    main()
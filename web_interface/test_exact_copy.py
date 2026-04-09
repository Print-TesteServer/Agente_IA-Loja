import sys
import os

# --- RESOLUÇÃO DE CAMINHO CRÍTICA ---
# Garante que a raiz do projeto esteja no path, não importa de onde o script seja rodado
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional

# Importação do Core (Cérebro)
from agent_core.agent import build_agent
from agent_core.tools import escalate_to_human

# Importação de utilitários do main.py na raiz
import main as main_module
_format_ai_response = main_module._format_ai_response
save_to_history = main_module.save_to_history
init_database = main_module.init_database
load_history = main_module.load_history

app = FastAPI(title="Agente IA Loja - Chat Web", version="1.0.0")

# Garante que a pasta static exista para não quebrar o mount
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Modelos Pydantic
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = "web-user"

class ChatResponse(BaseModel):
    response: str
    session_id: str

# Inicialização global
agent = build_agent()
init_database()

@app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    """Retorna a interface de chat HTML simples"""
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <title>Chat com Agente IA Loja</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f0f2f5; }
            .chat-container { background-color: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); height: 600px; display: flex; flex-direction: column; }
            .chat-messages { flex-grow: 1; overflow-y: auto; padding: 15px; border: 1px solid #e4e6eb; border-radius: 8px; margin-bottom: 15px; background-color: #fafafa; }
            .message { margin-bottom: 12px; padding: 10px 15px; border-radius: 18px; max-width: 75%; line-height: 1.4; }
            .user-message { background-color: #0084ff; color: white; align-self: flex-end; margin-left: auto; border-bottom-right-radius: 4px; }
            .bot-message { background-color: #e4e6eb; color: #050505; align-self: flex-start; border-bottom-left-radius: 4px; }
            .chat-input { display: flex; gap: 10px; }
            .chat-input input { flex-grow: 1; padding: 12px 18px; border: 1px solid #ddd; border-radius: 25px; outline: none; }
            .chat-input button { padding: 10px 25px; background-color: #0084ff; color: white; border: none; border-radius: 25px; cursor: pointer; font-weight: bold; }
            .chat-input button:hover { background-color: #0073e6; }
        </style>
    </head>
    <body>
        <h1 style="text-align: center; color: #1c1e21;">🤖 Assistente Virtual (Lia)</h1>
        <div class="chat-container">
            <div class="chat-messages" id="chatMessages">
                <div class="message bot-message">Olá! 👋 Sou a Lia. Como posso ajudar você com suas compras hoje?</div>
            </div>
            <div class="chat-input">
                <input type="text" id="userInput" placeholder="Pergunte sobre horários, trocas ou produtos..." autofocus />
                <button onclick="sendMessage()">Enviar</button>
            </div>
        </div>

        <script>
            function addMessage(content, isUser = false) {
                const chatMessages = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
                messageDiv.textContent = content;
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            async function sendMessage() {
                const userInput = document.getElementById('userInput');
                const message = userInput.value.trim();
                if (!message) return;

                addMessage(message, true);
                userInput.value = '';

                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: message, session_id: 'web-user' })
                    });
                    const data = await response.json();
                    addMessage(data.response, false);
                } catch (error) {
                    addMessage('Ops! Tive um problema técnico. Tente novamente em instantes.', false);
                }
            }

            document.getElementById('userInput').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """Endpoint para processar mensagens de chat com suporte a ferramentas"""
    try:
        user_input = chat_message.message.strip()
        session_id = chat_message.session_id or "web-user"

        if not user_input:
            raise HTTPException(status_code=400, detail="Mensagem vazia")

        # 1. Recupera histórico
        chat_history = []
        recent_messages = load_history(session_id, limit=5)
        from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

        for user_msg, ai_msg in reversed(recent_messages):
            chat_history.append(HumanMessage(content=user_msg))
            chat_history.append(AIMessage(content=ai_msg))

        chat_history.append(HumanMessage(content=user_input))

        # 2. Primeira execução
        response = agent.invoke({"messages": chat_history})

        # 3. Lógica de Tool Calling (Escalonamento)
        if hasattr(response, 'tool_calls') and response.tool_calls:
            available_tools = {"escalate_to_human": escalate_to_human}

            for tool_call in response.tool_calls:
                tool_name = tool_call["name"].lower()
                if tool_name in available_tools:
                    tool_result = available_tools[tool_name].invoke(tool_call["args"])

                    chat_history.append(response)
                    chat_history.append(ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=str(tool_result)
                    ))

                    # Chamada final após execução da tool
                    response = agent.invoke({"messages": chat_history})

        # 4. Finalização e Persistência
        final_text = _format_ai_response(response.content)
        save_to_history(session_id, user_input, final_text)

        return ChatResponse(response=final_text, session_id=session_id)

    except Exception as e:
        print(f"ERRO NO SERVIDOR: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar chat")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Agente IA Loja Chat Web"}

if __name__ == "__main__":
    print("Iniciando servidor de teste...")
    try:
        import uvicorn
        print("Uvicorn importado com sucesso")
        print("Iniciando servidor em 0.0.0.0:8000")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"Erro ao iniciar uvicorn: {e}")
        import traceback
        traceback.print_exc()
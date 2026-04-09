print("Testando endpoint de chat...")
import sys
import os

# --- RESOLUÇÃO DE CAMINHO CRÍTICA ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
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

    print("1. Todas as importações - OK")

    app = FastAPI(title="Agente IA Loja - Chat Web", version="1.0.0")
    print("2. Instância FastAPI criada - OK")

    # Garante que a pasta static exista para não quebrar o mount
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    print("3. Montagem de static files - OK")

    # Modelos Pydantic
    class ChatMessage(BaseModel):
        message: str
        session_id: Optional[str] = "web-user"

    class ChatResponse(BaseModel):
        response: str
        session_id: str

    print("4. Modelos Pydantic criados - OK")

    # Inicialização global
    print("5. Antes de build_agent()...")
    agent = build_agent()
    print("   build_agent() - OK")

    print("6. Antes de init_database()...")
    init_database()
    print("   init_database() - OK")

    # Testando endpoint de chat completo
    @app.post("/chat", response_model=ChatResponse)
    async def chat_endpoint(chat_message: ChatMessage):
        """Endpoint para processar mensagens de chat com suporte a ferramentas"""
        try:
            print(f"   Recebida mensagem: {chat_message.message}")
            user_input = chat_message.message.strip()
            session_id = chat_message.session_id or "web-user"

            if not user_input:
                raise HTTPException(status_code=400, detail="Mensagem vazia")

            # 1. Recupera histórico
            print("   Recuperando histórico...")
            chat_history = []
            recent_messages = load_history(session_id, limit=5)
            from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

            for user_msg, ai_msg in reversed(recent_messages):
                chat_history.append(HumanMessage(content=user_msg))
                chat_history.append(AIMessage(content=ai_msg))

            chat_history.append(HumanMessage(content=user_input))
            print(f"   Histórico criado com {len(chat_history)} mensagens")

            # 2. Primeira execução
            print("   Invocando agente...")
            response = agent.invoke({"messages": chat_history})
            print("   Agente invocado")

            # 3. Lógica de Tool Calling (Escalonamento)
            if hasattr(response, 'tool_calls') and response.tool_calls:
                print("   Processando tool calls...")
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
            print("   Formatando resposta...")
            final_text = _format_ai_response(response.content)
            save_to_history(session_id, user_input, final_text)
            print("   Resposta processada e salva")

            return ChatResponse(response=final_text, session_id=session_id)

        except Exception as e:
            print(f"ERRO NO ENDPOINT: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail="Erro interno ao processar chat")

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "Agente IA Loja Chat Web"}

    print("9. Endpoints definidos - OK")

    print("TESTE DE ENDPOINT DE CHAT COMPLETO - TUDO OK!")

except Exception as e:
    print(f"ERRO: {e}")
    import traceback
    traceback.print_exc()
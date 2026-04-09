print("Testando definição de rotas...")
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

    # Testando rota simples
    @app.get("/test")
    async def test_endpoint():
        return {"message": "teste OK"}

    print("7. Rota de teste definida - OK")

    # Testando rota HTML
    @app.get("/", response_class=HTMLResponse)
    async def get_chat_interface():
        html_content = "<h1>Teste HTML</h1>"
        return HTMLResponse(content=html_content)

    print("8. Rota HTML definida - OK")

    print("TESTE DE ROTAS COMPLETO - TUDO OK!")

    # Não vamos realmente executar o servidor, apenas testar se as rotas podem ser definidas

except Exception as e:
    print(f"ERRO: {e}")
    import traceback
    traceback.print_exc()
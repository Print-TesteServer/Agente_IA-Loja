#!/usr/bin/env python
"""
Script de inicialização para o interface web do Agente IA Loja
"""
import sys
import os

# Adiciona o diretório raiz ao path para permettre imports do agent_core e main
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

if __name__ == "__main__":
    import uvicorn
    print("Iniciando servidor web do Agente IA Loja...")
    print(f"Diretório atual: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}")
    try:
        uvicorn.run("web_interface.web_main:app", host="0.0.0.0", port=8000, reload=True)
        print("Servidor iniciado com sucesso!")
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
        import traceback
        traceback.print_exc()
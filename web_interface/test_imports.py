print("Testando importações...")
import sys
import os

print("1. Importando sys e os - OK")

# --- RESOLUÇÃO DE CAMINHO CRÍTICA ---
# Garante que a raiz do projeto esteja no path, não importa de onde o script seja rodado
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
print(f"2. current_dir: {current_dir}")
print(f"3. root_dir: {root_dir}")

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
    print("4. Adicionado root_dir ao sys.path")
else:
    print("4. root_dir já está no sys.path")

print(f"5. sys.path[0:3]: {sys.path[0:3]}")

try:
    print("6. Tentando importar FastAPI...")
    from fastapi import FastAPI, HTTPException
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse
    print("   FastAPI imports - OK")
except Exception as e:
    print(f"   ERRO no FastAPI: {e}")
    import traceback
    traceback.print_exc()

try:
    print("7. Tentando importar pydantic...")
    from pydantic import BaseModel
    from typing import Optional
    print("   Pydantic imports - OK")
except Exception as e:
    print(f"   ERRO no pydantic: {e}")

try:
    print("8. Tentando importar agent_core...")
    from agent_core.agent import build_agent
    from agent_core.tools import escalate_to_human
    print("   agent_core imports - OK")
except Exception as e:
    print(f"   ERRO no agent_core: {e}")
    import traceback
    traceback.print_exc()

try:
    print("9. Tentando importar main módulo...")
    import main as main_module
    _format_ai_response = main_module._format_ai_response
    save_to_history = main_module.save_to_history
    init_database = main_module.init_database
    load_history = main_module.load_history
    print("   main módulo imports - OK")
except Exception as e:
    print(f"   ERRO no main módulo: {e}")
    import traceback
    traceback.print_exc()

print("Teste de importações concluído")
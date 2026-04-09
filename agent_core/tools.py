import logging
from langchain.tools import tool
from pydantic import BaseModel, Field

# 1. Configuração de Logs Estruturados
# Usamos o nome do pacote para facilitar o rastreamento em logs complexos
logger = logging.getLogger("agent_core.tools")

# 2. Definição do Schema de Entrada (Validação de Dados)
class EscalateInput(BaseModel):
    reason: str = Field(
        description="O motivo detalhado do escalonamento (ex: tom agressivo, pedido de humano, fora do escopo)."
    )
    user_message: str = Field(
        default="",  # Torna o campo opcional para o validador Pydantic
        description="A mensagem exata enviada pelo usuário que gerou a necessidade de escalonamento."
    )

@tool("escalate_to_human", args_schema=EscalateInput)
def escalate_to_human(reason: str, user_message: str = "") -> str:
    """
    Acione esta ferramenta obrigatoriamente quando o cliente solicitar falar com um humano, 
    demonstrar irritação/agressividade ou fizer perguntas que não estão na base de conhecimento.
    """
    # 3. Simulação de Webhook (Saída no console para integração com N8N/Make)
    print(f"\n[SISTEMA] >> DISPARANDO WEBHOOK DE ESCALONAMENTO:")
    print(f"    Motivo : {reason}")
    print(f"    Cliente: {user_message}")
    
    logger.info(f"Escalonamento executado via Tool. Motivo: {reason}")
    
    return (
        f"Solicitação de escalonamento registrada com sucesso. Motivo: {reason}. "
        "Um atendente humano foi notificado e assumirá o chat em instantes."
    )
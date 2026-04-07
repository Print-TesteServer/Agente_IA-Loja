from langchain.tools import tool


@tool
def escalate_to_human(reason: str, user_message: str = "") -> str:
    """Chame esta ferramenta quando o cliente pedir um atendente humano,
    demonstrar tom agressivo ou quando a pergunta estiver fora da base
    de conhecimento.

    Args:
        reason: motivo do escalonamento (ex: "cliente pediu humano",
                "tom agressivo", "pergunta fora da base").
        user_message: mensagem original do cliente que motivou o escalonamento.
    """
    print(f"\n>> ENVIANDO WEBHOOK PARA N8N:")
    print(f"   Motivo : {reason}")
    print(f"   Cliente: {user_message}")
    return (
        f"Webhook enviado com sucesso. Motivo: {reason}. "
        "Um atendente humano entrará em contato."
    )

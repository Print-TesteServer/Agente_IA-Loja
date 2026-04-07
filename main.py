from langchain_core.messages import HumanMessage, AIMessage

from agent import build_agent


def _extract_text(content):
    """Extract text from AI message content, handling both plain strings
    and Gemini's list of content blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                parts.append(block.get("text", ""))
            elif hasattr(block, "text"):
                parts.append(block.text)
        return "\n".join(p for p in parts if p)
    return str(content)


def main():
    print("=== Assistente Virtual da Loja ===")
    print("Digite 'sair' para encerrar.\n")

    agent = build_agent()
    messages = []

    while True:
        user_input = input("Você: ").strip()
        if user_input.lower() in ("sair", "exit", "quit"):
            print("Até mais!")
            break
        if not user_input:
            continue

        messages.append(HumanMessage(content=user_input))
        result = agent.invoke({"messages": messages})

        # Extract the last AI message (skip HumanMessage, SystemMessage, ToolMessage)
        ai_messages = [
            m for m in result["messages"]
            if isinstance(m, AIMessage)
        ]
        output = _extract_text(ai_messages[-1].content) if ai_messages else "Sem resposta."
        print(f"\nAssistente: {output}")

        # Append the AI response to history
        if ai_messages:
            messages.append(ai_messages[-1])


if __name__ == "__main__":
    main()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from config import GOOGLE_API_KEY, MODEL, TEMPERATURE
from prompts import SYSTEM_PROMPT
from tools import escalate_to_human

def build_agent():
    # 1. Configuração do modelo
    # Usamos uma temperatura baixa (0.1) para garantir que as respostas nos 
    # testes sejam previsíveis e sigam à risca o SYSTEM_PROMPT.
    llm = ChatGoogleGenerativeAI(
        model=MODEL,
        temperature=0.1, 
        google_api_key=GOOGLE_API_KEY,
    )

    # 2. Definição das ferramentas (Tools)
    tools = [escalate_to_human]

    # 3. Vínculo Explícito (Tool Binding)
    # Aqui o LangChain converte sua função Python em um JSON Schema que o Gemini entende.
    llm_with_tools = llm.bind_tools(tools)

    # 4. Definição do Prompt estruturado
    # O MessagesPlaceholder é vital para a persistência, pois é onde o histórico entra.
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages"),
    ])

    # 5. Construção da Chain (Cadeia de execução)
    # A estrutura 'prompt | model' é o padrão moderno da LangChain 0.3+.
    agent = prompt | llm_with_tools

    return agent
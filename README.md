# Assistente de Atendimento Inteligente — Loja IA

Assistente de IA para atendimento de loja, construído com **LangChain** e **Google Gemini 2.5 Flash**.

## Estrutura do Projeto

```
.
├── config.py           # Carrega variáveis de ambiente (.env)
├── knowledge_base.py   # Base de conhecimento (horário, prazo, troca)
├── prompts.py          # System Prompt com persona e regras
├── tools.py            # Tool de escalonamento (webhook simulado)
├── agent.py            # Monta o agente LangChain
├── main.py             # Loop de conversação no terminal
├── tests/              # Testes unitários dos cenários avaliados
├── .env.example        # Modelo de variáveis de ambiente
└── requirements.txt    # Dependências
```

## Design do Prompt

O `System Prompt` foi construído com três pilares:

1. **Persona** — atendente educado, conciso e prestativo.
2. **Regra Anti-Alucinação** — o modelo só pode usar informações presentes na base de conhecimento. Se a pergunta estiver fora do escopo, ele deve usar a ferramenta de escalonamento ao invés de inventar uma resposta.
3. **Gatilho de Automação** — o modelo foi instruído a chamar `escalate_to_human` em três situações:
   - Cliente pede explicitamente um atendente humano.
   - Tom agressivo ou frustrado detectado.
   - Pergunta fora da base de conhecimento.

## Como Rodar

```bash
# 1. Instale as dependências
pip install -r requirements.txt

# 2. Configure sua chave da Google
cp .env.example .env
# Edite .env e coloque sua chave GOOGLE_API_KEY
# Obtenha em: https://aistudio.google.com/apikey

# 3. Execute
python main.py
```

## Testes

```bash
pytest tests/ -v
```

Os testes verificam:
- Presença dos campos obrigatórios na base de conhecimento.
- Regras de anti-alucinação e escalonamento no prompt.
- Funcionamento correto da tool de webhook.

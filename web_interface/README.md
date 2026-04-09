# Interface Web - Chat com Agente IA Loja

Esta é a interface web desenvolvida com FastAPI para interagir com o agente IA da loja.

## Funcionalidades

- Interface de chat responsiva e amigável
- Integração completa com o agente existente (mesma lógica do terminal)
- Persistência de histórico de conversas via SQLite
- Suporte a tool calling (ex: escalonamento para humano)
- Design clean e intuitivo

## Como executar

### Opção 1: Diretamente com Python
```bash
cd web_interface
python web_main.py
```

### Opção 2: Com Uvicorn (desenvolvimento)
```bash
cd web_interface
uvicorn web_main:app --reload --host 0.0.0.0 --port 8000
```

### Opção 3: Produção
```bash
cd web_interface
uvicorn web_main:app --host 0.0.0.0 --port 8000
```

## Endpoints da API

- `GET /` - Interface de chat HTML
- `POST /chat` - Enviar mensagem e receber resposta do agente
- `GET /health` - Verificação de saúde do serviço

## Tecnologias utilizadas

- FastAPI - Framework web moderno e rápido
- Uvicorn - Servidor ASGI
- HTML/CSS/JavaScript vanilla - Interface frontend simples
- SQLite - Persistência de histórico
- LangChain - Integração com o agente existente

## Estrutura do projeto

```
web_interface/
├── main.py              # Aplicação FastAPI principal
├── static/              # Arquivos estáticos (CSS, JS, imagens)
└── README.md           # Este arquivo
```

## Integração com o agente existente

A interface web reutiliza exatamente a mesma lógica do agente presente em `main.py`:

- Mesma inicialização do agente via `build_agent()`
- Mesmo processo de tool calling e execução
- Mesmo formato de resposta e tratamento de conteúdo
- Mesmo sistema de persistência de histórico no banco SQLite
- Mesma função de formatação de resposta (`_format_ai_response`)
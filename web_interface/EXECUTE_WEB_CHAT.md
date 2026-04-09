# Como Executar o Chat Web FASTAPI

## Pré-requisitos

Certifique-se de que todas as dependências estão instaladas:
```bash
pip install -r requirements.txt
```

## Executando a Aplicação

### Opção 1: Executando diretamente (recomendado para teste)
```bash
# Acesse o diretorio da interface web
cd web_interface

# Execute a aplicação
python web_main.py
```

### Opção 2: Usando Uvicorn diretamente
```bash
cd web_interface
uvicorn web_main:app --reload --host 0.0.0.0 --port 8000
```

### Opção 3: Para ambiente de produção
```bash
cd web_interface
uvicorn web_main:app --host 0.0.0.0 --port 8000
```

## Acessando a Interface

Após iniciar o servidor, abra seu navegador e acesse:
```
http://localhost:8000
```

Você verá uma interface de chat simples onde pode interagir com o agente IA da loja.

## Funcionalidades Implementadas

✅ Interface de chat web responsiva  
✅ Integração completa com o agente existente (mesma lógica do terminal)  
✅ Persistência de histórico de conversas via SQLite  
✅ Suporte a tool calling (ex: escalonamento para humano)  
✅ Design clean e intuitivo  
✅ Endpoint de saúde (/health) para monitoramento  

## Tecnologias Utilizadas

- **FastAPI**: Framework web moderno e assíncrono
- **Uvicorn**: Servidor ASGI de alta performance
- **HTML/CSS/JS Vanilla**: Interface frontend simples e eficaz
- **SQLite**: Banco de dados leve para persistência de histórico
- **LangChain**: Reutilização direta do agente existente

## Estrutura de Arquivos

```
web_interface/
├── main.py              # Aplicação FastAPI principal
├── static/              # Diretório para arquivos estáticos (futuro)
├── teste.py             # Arquivo de teste (pode ser removido)
└── README.md           # Documentação da interface web
```

## Integração com o Código Existente

A interface web foi projetada para reutilizar exatamente a mesma lógica do agente presente no código original:

- Usa a mesma função `build_agent()` do arquivo `agent.py`
- Reutiliza o mesmo processo de tool calling e execução
- Mantém o mesmo formato de resposta e tratamento de conteúdo
- Utiliza o mesmo sistema de persistência de histórico no banco SQLite
- Aplica a mesma função de formatação de resposta (`_format_ai_response` do `main.py`)

Isso garante que o comportamento do agente seja idêntico zarówno na interface de terminal quanto na interface web.

## Endpoints da API

- **GET /** - Retorna a interface de chat HTML
- **POST /chat** - Recebe mensagens e retorna respostas do agente (JSON)
- **GET /health** - Endpoint de verificação de saúde do serviço

## Personalização Futura

Para personalizar a interface, você pode:
1. Modificar o HTML retornado no endpoint `/` em `web_interface/main.py`
2. Adicionar arquivos CSS e JS no diretório `static/` e servir via `StaticFiles`
3. Estender os modelos Pydantic para suportar mais tipos de dados
4. Adicionar autenticação se necessário para ambientes de produção
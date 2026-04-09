Aqui está a versão atualizada e profissional do seu **README.md**. Adicionei os detalhes técnicos sobre a memória de identidade, a persistência de sessão fixa para testes e organizei os pilares de arquitetura para destacar seu domínio técnico.

---

# Assistente de Atendimento Inteligente — Loja IA

Assistente de IA conversacional para atendimento ao cliente, desenvolvido com **LangChain** e **Google Gemini 1.5 Flash**. O projeto foca em segurança (anti-alucinação), memória persistente e escalabilidade.

## 🎯 Status do Projeto: **MELHORIAS CONCLUÍDAS**

✅ **Cache do LangChain** - Implementado para otimização de custos e performance.  
✅ **Persistência SQLite** - Histórico de conversas mantido entre reinicializações.  
✅ **Memória de Identidade** - Capacidade de lembrar o nome e contexto do usuário.  
✅ **Arquitetura RAG-Ready** - Estrutura preparada para busca semântica (Vector Stores).

---

## 📋 Estrutura do Projeto

```text
.
├── agent.py            # Orquestração do agente e configuração de Cache
├── config.py           # Gestão de variáveis de ambiente e Hiperparâmetros
├── knowledge_base.py   # Base de conhecimento estruturada (Dicionário)
├── main.py             # Interface CLI com gestão de sessão e persistência SQLite
├── prompts.py          # System Prompt, definições de Persona e regras de memória
├── tools.py            # Definição de ferramentas (Webhook de Escalonamento)
├── tests/              # Suíte de testes automatizados (Pytest)
├── web_interface/      # Interface web com FastAPI para chat
│   ├── main.py         # Aplicação FastAPI principal
│   ├── static/         # Arquivos estáticos (CSS, JS, imagens)
│   └── README.md       # Documentação da interface web
├── .env.example        # Template para chaves de API
├── .gitignore          # Proteção de arquivos sensíveis e binários
└── RELATIVO_FINAL.md   # Relatório técnico consolidado
```

---

## 🚀 Diferenciais Técnicos

### 🧠 Memória e Gestão de Identidade
Diferente de implementações básicas, este assistente utiliza um `session_id` persistente atrelado a um banco de dados **SQLite**.
- **Continuidade**: O usuário pode encerrar o programa e, ao retornar, a Lia lembrará seu nome e o histórico das últimas interações.
- **Contexto**: Instruções específicas no `SYSTEM_PROMPT` garantem que a IA utilize o histórico para um atendimento personalizado.

### 🛡️ Camada de Segurança (Anti-Alucinação)
O sistema opera sob o princípio de **conhecimento fechado**:
- Respostas limitadas estritamente à `knowledge_base.py`.
- **Escalonamento Inteligente**: Uso da tool `escalate_to_human` em casos de perguntas fora de escopo, detecção de frustração ou solicitação direta do cliente.

### ⚡ Performance com LLM Cache
Implementação de `InMemoryCache` para mitigar o erro `429 RESOURCE_EXHAUSTED` (Rate Limit) e reduzir a latência em perguntas repetitivas, economizando tokens da API.

---

## ▶️ Como Rodar

### 1. Preparação do Ambiente
```bash
# Clone o repositório e instale as dependências
pip install -r requirements.txt
```

### 2. Configuração
Crie um arquivo `.env` na raiz do projeto com sua chave:
```env
GOOGLE_API_KEY=sua_chave_aqui
MODEL=gemini-1.5-flash
TEMPERATURE=0.1
```

### 3. Execução da Interface CLI (Terminal)
```bash
python main.py
```
*Nota: Para testes de persistência, o `session_id` está fixado como `test-user` no `main.py`.*

### 4. Execução da Interface Web (FASTAPI)
```bash
# Acesse o diretório da interface web
cd web_interface

# Execute a aplicação
python main.py
```
*Alternativa com Uvicorn:*
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
*Em seguida, acesse http://localhost:8000 no seu navegador*

---

## ✅ Validação e Testes

O projeto conta com uma cobertura de testes rigorosa para garantir que as regras de negócio sejam respeitadas.

```bash
pytest tests/ -v
```

**Resultados obtidos:**
- **19/19 TESTES PASSANDO** (100% de cobertura dos cenários críticos).
- Validação de: Fluxo de Webhook, Anti-alucinação, Persona e Integridade da Base de Conhecimento.

---

## 🔮 Próximos Passos (Roadmap de Escala)
O projeto foi desenhado para crescer sem refatoração profunda:
1. **✅ Fase Web CONCLUÍDA**: Implementação de API com **FastAPI** disponível em `/web_interface`
2. **Busca Semântica**: Integração com **ChromaDB** quando a base superar 30 artigos.
3. **Multi-tenancy**: Gestão de sessões por `user_id` via cabeçalhos HTTP.

---
**Desenvolvido por Matheus Ferreira** *Foco em Engenharia de Prompt e Automação de Processos.*
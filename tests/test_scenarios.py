import pytest
from unittest.mock import patch

from tools import escalate_to_human
from prompts import SYSTEM_PROMPT
from knowledge_base import KNOWLEDGE_BASE


class TestKnowledgeBase:
    """Garante que a base de conhecimento contém os campos exigidos e conteúdo válido."""

    def test_has_horario(self):
        assert "horario_funcionamento" in KNOWLEDGE_BASE

    def test_has_prazo(self):
        assert "prazo_entrega" in KNOWLEDGE_BASE

    def test_has_politica(self):
        assert "politica_troca" in KNOWLEDGE_BASE

    def test_horario_content(self):
        value = KNOWLEDGE_BASE["horario_funcionamento"].lower()
        assert "segunda" in value or "09h" in value

    def test_prazo_content(self):
        value = KNOWLEDGE_BASE["prazo_entrega"].lower()
        assert "5" in value and "dia" in value

    def test_troca_content(self):
        value = KNOWLEDGE_BASE["politica_troca"].lower()
        assert "7" in value and "dia" in value


class TestSystemPrompt:
    """
    Testa a qualidade e completude do System Prompt.

    Valida que o prompt contém:
    - Instruções anti-alucinação (não inventar informações)
    - Gatilhos de escalonamento (quando chamar a tool)
    - Definição clara da persona
    """

    def test_anti_hallucination_instruction(self):
        """
        Verifica se o prompt instrui o modelo a não inventar informações.

        O prompt deve conter variações como "nunca invente", "não crie",
        ou "só responda usando as informações disponíveis".
        """
        prompt_lower = SYSTEM_PROMPT.lower()

        # Verifica instruções explícitas contra alucinação
        anti_hallucination_phrases = [
            "nunca invente",
            "não invente",
            "não crie",
            "só responda usando",
            "informações disponíveis"
        ]

        found = any(phrase in prompt_lower for phrase in anti_hallucination_phrases)
        assert found, "Prompt deve instruir o modelo a não inventar informações"

    def test_escalation_triggers_defined(self):
        """
        Verifica se o prompt define quando acionar o escalonamento.

        Deve mencionar pelo menos um gatilho:
        - Pedido de atendente humano
        - Tom agressivo/frustrado
        - Pergunta fora da base de conhecimento
        """
        prompt_lower = SYSTEM_PROMPT.lower()

        # Gatilhos de escalonamento
        escalation_triggers = {
            "humano": "atendente humano" in prompt_lower or "falar com humano" in prompt_lower,
            "agressivo": "agressivo" in prompt_lower or "frustrado" in prompt_lower or "raiva" in prompt_lower,
            "fora_da_base": "fora" in prompt_lower or "não está coberta" in prompt_lower,
        }

        # Deve ter pelo menos 2 gatilhos definidos
        assert sum(escalation_triggers.values()) >= 2, \
            "Prompt deve definir pelo menos 2 gatilhos de escalonamento"

    def test_persona_traits_defined(self):
        """
        Verifica se a persona está bem definida com traits específicos.

        Uma boa persona deve ter pelo menos 3 traits definidos.
        """
        prompt_lower = SYSTEM_PROMPT.lower()

        # Traits esperadas para uma atendente de loja
        persona_traits = {
            "simpatia": "simpatia" in prompt_lower,
            "acolhedor": "acolhedor" in prompt_lower,
            "empático": "empático" in prompt_lower or "empatia" in prompt_lower,
            "humanizada": "humanizada" in prompt_lower or "humanizado" in prompt_lower,
            "educado": "educado" in prompt_lower or "polite" in prompt_lower,
            "conciso": "conciso" in prompt_lower or "concisa" in prompt_lower,
        }

        # Deve ter pelo menos 3 traits definidos
        trait_count = sum(persona_traits.values())
        assert trait_count >= 3, \
            f"Persona deve ter pelo menos 3 traits (encontradas: {trait_count})"

    def test_escalation_tool_referenced(self):
        """
        Verifica se o prompt referencia corretamente a tool de escalonamento.

        O prompt deve mencionar o nome da tool ou "ferramenta".
        """
        has_tool_name = "escalate_to_human" in SYSTEM_PROMPT
        has_tool_reference = "ferramenta" in SYSTEM_PROMPT.lower()

        assert has_tool_name or has_tool_reference, \
            "Prompt deve referenciar a tool de escalonamento"

    def test_no_contradictory_instructions(self):
        """
        Verifica se não há instruções contraditórias no prompt.

        Um prompt não deve dizer para "sempre responder" e "não responder" ao mesmo tempo.
        """
        prompt_lower = SYSTEM_PROMPT.lower()

        # Verifica se há instruções de "sempre" junto com "nunca" para o mesmo contexto
        has_always = "sempre" in prompt_lower
        has_never = "nunca" in prompt_lower or "não" in prompt_lower

        # Se tiver ambos, não é necessariamente erro, mas vale a pena verificar
        # que não são contraditórios (ex: "sempre responda" e "nunca responda")
        if has_always and has_never:
            # Verifica se as instruções não são diretamente contraditórias
            assert "sempre responda" not in prompt_lower or "nunca responda" not in prompt_lower, \
                "Prompt contém instruções contraditórias"


class TestEscalationTool:
    """
    Testa a tool de escalonamento (escalate_to_human).

    Valida que a tool:
    - Imprime o webhook no console
    - Retorna mensagem de sucesso
    - Aceita diferentes motivos de escalonamento
    - Funciona com parâmetros opcionais
    """

    def test_prints_webhook_message(self, capsys):
        """
        Verifica se a tool imprime a mensagem de webhook no console.

        Esta é a simulação do envio para n8n/Make.
        """
        result = escalate_to_human.invoke({
            "reason": "cliente pediu humano",
            "user_message": "Quero falar com um atendente!",
        })
        captured = capsys.readouterr()

        assert "ENVIANDO WEBHOOK" in captured.out, \
            "Tool deve imprimir 'ENVIANDO WEBHOOK'"
        assert "cliente pediu humano" in captured.out, \
            "Tool deve imprimir o motivo do escalonamento"
        assert "sucesso" in result.lower(), \
            "Tool deve retornar mensagem de sucesso"

    def test_escalation_reasons(self, capsys):
        """
        Testa diferentes motivos de escalonamento.

        Motivos válidos incluem:
        - Tom agressivo do cliente
        - Pergunta fora da base de conhecimento
        - Pedido explícito de atendente humano
        """
        reasons = [
            ("tom agressivo", "Isso é um absurdo!"),
            ("pergunta fora da base", "Qual o CNPJ da loja?"),
            ("pedido de humano", "Quero falar com um atendente"),
        ]
        for reason, message in reasons:
            result = escalate_to_human.invoke({
                "reason": reason,
                "user_message": message,
            })
            assert "sucesso" in result.lower(), \
                f"Tool deve retornar sucesso para motivo: {reason}"

    def test_handles_optional_user_message(self, capsys):
        """
        Verifica que a tool funciona mesmo sem user_message.

        O parâmetro user_message é opcional na definição da tool.
        """
        result = escalate_to_human.invoke({
            "reason": "cliente não respondeu"
        })
        assert "sucesso" in result.lower(), \
            "Tool deve funcionar sem user_message"

    def test_tool_has_langchain_attributes(self):
        """
        Verifica que a tool está corretamente decorada para LangChain.

        Uma tool do LangChain deve ter:
        - name: nome da tool
        - description: descrição do que a tool faz
        - args_schema: schema dos argumentos (opcional, mas recomendado)
        """
        assert hasattr(escalate_to_human, 'name'), \
            "Tool deve ter atributo 'name'"
        assert hasattr(escalate_to_human, 'description'), \
            "Tool deve ter atributo 'description'"
        assert escalate_to_human.name == "escalate_to_human", \
            "Tool deve ter nome 'escalate_to_human'"

    def test_tool_description_mentions_triggers(self):
        """
        Verifica se a descrição da tool menciona quando usá-la.

        A descrição deve mencionar pelo menos um gatilho:
        - humano, agressivo, fora da base
        """
        description = escalate_to_human.description.lower()

        triggers = ["humano", "agressivo", "fora", "base"]
        found = any(t in description for t in triggers)

        assert found, \
            "Descrição da tool deve mencionar quando usá-la"


class TestIntegrationScenarios:
    """
    Testa cenários de integração que combinam múltiplos componentes.

    Estes testes validam que os componentes trabalham juntos corretamente.
    """

    def test_knowledge_base_has_all_required_info(self):
        """
        Verifica que a base de conhecimento tem TODAS as informações exigidas.

        Requisitos do projeto:
        - Horário de funcionamento (Seg-Sex, 09h às 18h)
        - Prazo de entrega (até 5 dias úteis)
        - Política de troca (7 dias após recebimento)
        """
        # Horário: deve mencionar segunda a sexta e 09h-18h
        horario = KNOWLEDGE_BASE["horario_funcionamento"].lower()
        assert "segunda" in horario and "sexta" in horario, \
            "Horário deve mencionar segunda a sexta"
        assert "09h" in horario and "18h" in horario, \
            "Horário deve mencionar 09h às 18h"

        # Prazo: deve mencionar 5 dias úteis
        prazo = KNOWLEDGE_BASE["prazo_entrega"].lower()
        assert "5" in prazo and "dia" in prazo, \
            "Prazo deve mencionar 5 dias"

        # Política: deve mencionar 7 dias e troca/devolução
        politica = KNOWLEDGE_BASE["politica_troca"].lower()
        assert "7" in politica and "dia" in politica, \
            "Política deve mencionar 7 dias"
        assert "troca" in politica or "devolução" in politica, \
            "Política deve mencionar troca ou devolução"

    def test_prompt_and_tool_are_aligned(self):
        """
        Verifica se o prompt e a tool estão alinhados.

        O prompt deve instruir a usar a mesma tool que está registrada.
        """
        # A tool deve ser mencionada no prompt
        tool_name = escalate_to_human.name
        assert tool_name in SYSTEM_PROMPT or "ferramenta" in SYSTEM_PROMPT.lower(), \
            f"Prompt deve mencionar a tool '{tool_name}'"

    def test_escalation_flow_simulation(self, capsys):
        """
        Simula o fluxo completo de escalonamento.

        Este teste simula o que aconteceria quando:
        1. Cliente faz pergunta fora do escopo
        2. Agente identifica e chama escalate_to_human
        3. Webhook é "enviado" (impresso no console)
        """
        # Simula a chamada que o agente faria
        reason = "pergunta fora da base de conhecimento"
        user_message = "Qual é o CNPJ da loja?"

        result = escalate_to_human.invoke({
            "reason": reason,
            "user_message": user_message,
        })

        captured = capsys.readouterr()

        # Verifica o fluxo completo
        assert "ENVIANDO WEBHOOK" in captured.out, \
            "Deve imprimir mensagem de webhook"
        assert reason in captured.out, \
            "Deve imprimir o motivo"
        assert user_message in captured.out, \
            "Deve imprimir a mensagem do cliente"
        assert "sucesso" in result.lower(), \
            "Deve retornar sucesso"

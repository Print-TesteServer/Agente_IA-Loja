import pytest
from unittest.mock import patch

from tools import escalate_to_human
from prompts import SYSTEM_PROMPT
from knowledge_base import KNOWLEDGE_BASE


class TestKnowledgeBase:
    """Garante que a base de conhecimento contém os campos exigidos."""

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


class TestPrompts:
    """Verifica que o prompt contém as regras exigidas."""

    def test_no_hallucination_rule(self):
        assert "NÃO invente" in SYSTEM_PROMPT or "NÃO crie" in SYSTEM_PROMPT

    def test_escalation_rule(self):
        assert "escalate_to_human" in SYSTEM_PROMPT or "ferramenta" in SYSTEM_PROMPT.lower()

    def test_persona_defined(self):
        system_lower = SYSTEM_PROMPT.lower()
        assert "educado" in system_lower or "polite" in system_lower


class TestEscalationTool:
    """Testa a tool de escalonamento."""

    def test_prints_webhook(self, capsys):
        result = escalate_to_human.invoke({
            "reason": "cliente pediu humano",
            "user_message": "Quero falar com um atendente!",
        })
        captured = capsys.readouterr()

        assert "ENVIANDO WEBHOOK" in captured.out
        assert "cliente pediu humano" in captured.out
        assert "sucesso" in result.lower()

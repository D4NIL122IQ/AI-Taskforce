"""
Tests unitaires pour back/modeles/LLMFactory.py

Stratégie : on mocke les constructeurs LangChain pour éviter
tout appel réseau réel. On vérifie uniquement que :
  1. La bonne classe est instanciée selon config.modele
  2. temperature et max_token sont bien transmis
  3. Les cas d erreur lèvent ValueError
"""

import pytest
from unittest.mock import patch, MagicMock
from back.modeles.LLMFactory import llmFactory, LLMConfig

def make_config(modele: str, temperature: float = 0.5, max_token: int = 500) -> LLMConfig:
    return LLMConfig(temperature=temperature, max_token=max_token, modele=modele)


class TestLLMFactoryModelesSupported:

    @patch("back.modeles.LLMFactory.ChatGoogleGenerativeAI")
    def test_gemini_instancie_correctement(self, mock_cls):
        mock_cls.return_value = MagicMock()
        result = llmFactory.initialise_llm(make_config("gemini"))
        mock_cls.assert_called_once_with(
            model="gemini-3-flash-preview",
            temperature=0.5,
            max_tokens=500
        )
        assert result is mock_cls.return_value

    @patch("back.modeles.LLMFactory.ChatOpenAI")
    def test_openai_instancie_correctement(self, mock_cls):
        mock_cls.return_value = MagicMock()
        result = llmFactory.initialise_llm(make_config("openai"))
        mock_cls.assert_called_once_with(
            model="gpt-4o-mini",
            temperature=0.5,
            max_tokens=500
        )
        assert result is mock_cls.return_value

    @patch("back.modeles.LLMFactory.ChatOllama")
    def test_ollama_instancie_correctement(self, mock_cls):
        mock_cls.return_value = MagicMock()
        llmFactory.initialise_llm(make_config("ollama"))
        mock_cls.assert_called_once()

    @patch("back.modeles.LLMFactory.ChatOllama")
    def test_mistral_utilise_chatollama(self, mock_cls):
        mock_cls.return_value = MagicMock()
        llmFactory.initialise_llm(make_config("mistral"))
        mock_cls.assert_called_once()

    @patch("back.modeles.LLMFactory.ChatDeepSeek")
    def test_deepseek_instancie_correctement(self, mock_cls):
        mock_cls.return_value = MagicMock()
        result = llmFactory.initialise_llm(make_config("deepseek"))
        mock_cls.assert_called_once_with(
            model="deepseek-chat",
            temperature=0.5,
            max_tokens=500,
            timeout=None,
            max_retries=2
        )
        assert result is mock_cls.return_value

    @patch("back.modeles.LLMFactory.ChatAnthropic")
    def test_anthropic_instancie_correctement(self, mock_cls):
        mock_cls.return_value = MagicMock()
        result = llmFactory.initialise_llm(make_config("anthropic"))
        mock_cls.assert_called_once_with(
            model="claude-3-haiku-20240307",
            temperature=0.5,
            max_tokens=500
        )
        assert result is mock_cls.return_value


class TestLLMFactoryCaseInsensitive:

    @patch("back.modeles.LLMFactory.ChatOpenAI")
    def test_openai_majuscules_accepte(self, mock_cls):
        mock_cls.return_value = MagicMock()
        llmFactory.initialise_llm(make_config("OPENAI"))
        mock_cls.assert_called_once()

    @patch("back.modeles.LLMFactory.ChatGoogleGenerativeAI")
    def test_gemini_mixte_accepte(self, mock_cls):
        mock_cls.return_value = MagicMock()
        llmFactory.initialise_llm(make_config("Gemini"))
        mock_cls.assert_called_once()


class TestLLMFactoryErreurs:

    def test_modele_inconnu_leve_value_error(self):
        with pytest.raises(ValueError, match="Modèle non supporté"):
            llmFactory.initialise_llm(make_config("modele_inexistant"))

    def test_modele_vide_leve_value_error(self):
        with pytest.raises(ValueError, match="doit être spécifié"):
            llmFactory.initialise_llm(make_config(""))

    def test_modele_none_leve_value_error(self):
        config = LLMConfig(temperature=0.5, max_token=500, modele=None)
        with pytest.raises(ValueError):
            llmFactory.initialise_llm(config)


class TestLLMConfig:

    def test_creation_standard(self):
        config = LLMConfig(temperature=0.7, max_token=1024, modele="openai")
        assert config.temperature == 0.7
        assert config.max_token == 1024
        assert config.modele == "openai"

    def test_temperature_zero(self):
        config = LLMConfig(temperature=0.0, max_token=100, modele="gemini")
        assert config.temperature == 0.0

    def test_temperature_un(self):
        config = LLMConfig(temperature=1.0, max_token=100, modele="gemini")
        assert config.temperature == 1.0

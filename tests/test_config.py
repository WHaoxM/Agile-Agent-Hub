import os
import pytest
from src.config import LLMConfig, get_llm_config


def test_llm_config_default_values():
    config = LLMConfig(api_key="test-key")
    assert config.api_key == "test-key"
    assert config.base_url is None
    assert config.model == "gpt-3.5-turbo"
    assert config.timeout == 30


def test_llm_config_custom_values():
    config = LLMConfig(
        api_key="test-key",
        base_url="https://api.example.com",
        model="gpt-4",
        timeout=60
    )
    assert config.api_key == "test-key"
    assert config.base_url == "https://api.example.com"
    assert config.model == "gpt-4"
    assert config.timeout == 60


def test_get_llm_config_from_env(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "env-api-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://env.example.com")
    monkeypatch.setenv("LLM_MODEL", "gpt-4-turbo")
    monkeypatch.setenv("LLM_TIMEOUT", "45")
    
    config = get_llm_config()
    assert config.api_key == "env-api-key"
    assert config.base_url == "https://env.example.com"
    assert config.model == "gpt-4-turbo"
    assert config.timeout == 45


def test_get_llm_config_missing_api_key(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    
    with pytest.raises(ValueError, match="LLM_API_KEY environment variable is required"):
        get_llm_config()


def test_get_llm_config_invalid_timeout(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_TIMEOUT", "not-a-number")
    
    config = get_llm_config()
    assert config.timeout == 30


def test_get_llm_config_default_model(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.delenv("LLM_MODEL", raising=False)
    
    config = get_llm_config()
    assert config.model == "gpt-3.5-turbo"


def test_get_llm_config_default_base_url(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    
    config = get_llm_config()
    assert config.base_url is None

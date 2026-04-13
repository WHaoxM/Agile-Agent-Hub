import pytest
from unittest import mock
from src.llm_client import call_llm_for_task_extraction, LLMClientError
from src.config import LLMConfig


def test_call_llm_with_empty_chat_text():
    config = LLMConfig(api_key="test-key")
    with pytest.raises(LLMClientError, match="chat_text cannot be empty"):
        call_llm_for_task_extraction("", config)


@mock.patch("src.llm_client.openai.OpenAI")
def test_call_llm_success(mock_openai):
    mock_response = mock.Mock()
    mock_choice = mock.Mock()
    mock_message = mock.Mock()
    mock_message.content = '''[
      {
        "task": "写API文档",
        "assignee": "张三",
        "deadline": "2026-04-14 15:00",
        "raw_text": "@张三 明天下午3点前把API文档写好"
      }
    ]'''
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    mock_client = mock.Mock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    config = LLMConfig(api_key="test-key")
    result = call_llm_for_task_extraction("@张三 写API文档", config)
    
    assert "写API文档" in result
    mock_client.chat.completions.create.assert_called_once()


@mock.patch("src.llm_client.openai.OpenAI")
def test_call_llm_no_choices(mock_openai):
    mock_response = mock.Mock()
    mock_response.choices = []
    
    mock_client = mock.Mock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    config = LLMConfig(api_key="test-key")
    with pytest.raises(LLMClientError, match="No choices in LLM response"):
        call_llm_for_task_extraction("@张三 写API文档", config)


@mock.patch("src.llm_client.openai.OpenAI")
def test_call_llm_empty_content(mock_openai):
    mock_response = mock.Mock()
    mock_choice = mock.Mock()
    mock_message = mock.Mock()
    mock_message.content = None
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    mock_client = mock.Mock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    config = LLMConfig(api_key="test-key")
    with pytest.raises(LLMClientError, match="Empty content in LLM response"):
        call_llm_for_task_extraction("@张三 写API文档", config)


@mock.patch("src.llm_client.openai.OpenAI")
def test_call_llm_api_error(mock_openai):
    from openai import APIError
    
    mock_client = mock.Mock()
    mock_client.chat.completions.create.side_effect = APIError("API error", request=None, body=None)
    mock_openai.return_value = mock_client
    
    config = LLMConfig(api_key="test-key")
    with pytest.raises(LLMClientError, match="LLM API error"):
        call_llm_for_task_extraction("@张三 写API文档", config)


@mock.patch("src.llm_client.openai.OpenAI")
def test_call_llm_timeout_error(mock_openai):
    from openai import APITimeoutError
    
    mock_client = mock.Mock()
    mock_client.chat.completions.create.side_effect = APITimeoutError("Request timed out.")
    mock_openai.return_value = mock_client
    
    config = LLMConfig(api_key="test-key")
    with pytest.raises(LLMClientError, match="LLM API timeout"):
        call_llm_for_task_extraction("@张三 写API文档", config)


@mock.patch("src.llm_client.openai.OpenAI")
def test_call_llm_connection_error(mock_openai):
    from openai import APIConnectionError
    
    mock_client = mock.Mock()
    mock_client.chat.completions.create.side_effect = Exception("connection error")
    mock_openai.return_value = mock_client
    
    config = LLMConfig(api_key="test-key")
    with pytest.raises(LLMClientError):
        call_llm_for_task_extraction("@张三 写API文档", config)


@mock.patch("src.llm_client.openai.OpenAI")
def test_call_llm_authentication_error(mock_openai):
    from openai import AuthenticationError
    
    mock_client = mock.Mock()
    mock_client.chat.completions.create.side_effect = Exception("auth error")
    mock_openai.return_value = mock_client
    
    config = LLMConfig(api_key="test-key")
    with pytest.raises(LLMClientError):
        call_llm_for_task_extraction("@张三 写API文档", config)


@mock.patch("src.llm_client.get_llm_config")
@mock.patch("src.llm_client.openai.OpenAI")
def test_call_llm_uses_default_config(mock_openai, mock_get_config):
    mock_response = mock.Mock()
    mock_choice = mock.Mock()
    mock_message = mock.Mock()
    mock_message.content = '[{"task": "test", "raw_text": "test"}]'
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    mock_client = mock.Mock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    mock_config = LLMConfig(api_key="default-key")
    mock_get_config.return_value = mock_config
    
    result = call_llm_for_task_extraction("test")
    
    mock_get_config.assert_called_once()
    assert "test" in result


@mock.patch("src.llm_client.openai.OpenAI")
def test_call_llm_with_base_url(mock_openai):
    mock_response = mock.Mock()
    mock_choice = mock.Mock()
    mock_message = mock.Mock()
    mock_message.content = '[{"task": "test", "raw_text": "test"}]'
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    mock_client = mock.Mock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    config = LLMConfig(
        api_key="test-key",
        base_url="https://custom.api.com/v1"
    )
    call_llm_for_task_extraction("test", config)
    
    call_args = mock_openai.call_args
    assert call_args[1]["base_url"] == "https://custom.api.com/v1"

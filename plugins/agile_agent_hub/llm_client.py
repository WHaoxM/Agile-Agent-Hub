from typing import Optional
from datetime import datetime
import openai
from .prompt import build_task_extraction_prompt, build_context_aware_prompt, build_group_chat_summary_prompt


class LLMClientError(Exception):
    pass


def call_llm_for_task_extraction(
    chat_text: str,
    api_base: str,
    api_key: str,
    model: str,
    timeout: int = 30
) -> str:
    if not chat_text:
        raise LLMClientError("chat_text cannot be empty")
    
    if not api_key:
        raise LLMClientError("api_key cannot be empty")
    
    if not model:
        raise LLMClientError("model cannot be empty")
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    prompt = build_task_extraction_prompt(chat_text, current_date)
    
    client_kwargs = {
        "api_key": api_key,
        "timeout": timeout
    }
    
    if api_base:
        client_kwargs["base_url"] = api_base
    
    try:
        client = openai.OpenAI(**client_kwargs)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的任务提取助手。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.0
        )
        
        if not response.choices:
            raise LLMClientError("No choices in LLM response")
        
        content = response.choices[0].message.content
        if not content:
            raise LLMClientError("Empty content in LLM response")
        
        return content.strip()
    
    except openai.APITimeoutError as e:
        raise LLMClientError(f"LLM API timeout: {e}") from e
    except openai.APIConnectionError as e:
        raise LLMClientError(f"LLM API connection error: {e}") from e
    except openai.AuthenticationError as e:
        raise LLMClientError(f"LLM API authentication error: {e}") from e
    except openai.APIError as e:
        raise LLMClientError(f"LLM API error: {e}") from e
    except Exception as e:
        raise LLMClientError(f"Unexpected error calling LLM: {e}") from e


def call_llm_for_context_aware_extraction(
    chat_text: str,
    api_base: str,
    api_key: str,
    model: str,
    timeout: int = 30
) -> str:
    """从聊天文本中进行上下文感知的任务提取。
    
    该函数使用 build_context_aware_prompt 构建提示词，
    引导 LLM 理解对话上下文、识别指代关系并提取任务。
    
    Args:
        chat_text: 聊天文本内容，不能为空字符串
        api_base: API 基础 URL
        api_key: API 密钥
        model: 模型名称
        timeout: 请求超时时间（秒），默认为 30
    
    Returns:
        LLM 返回的任务提取结果字符串（JSON 格式）
    
    Raises:
        LLMClientError: 当输入无效、API 调用失败或响应格式不正确时
        TypeError: 当 chat_text 或 config 类型不正确时
    """
    if not chat_text:
        raise LLMClientError("chat_text cannot be empty")
    
    if not isinstance(chat_text, str):
        raise TypeError(f"chat_text must be a string, got {type(chat_text).__name__}")
    
    if not api_key:
        raise LLMClientError("api_key cannot be empty")
    
    if not model:
        raise LLMClientError("model cannot be empty")
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    prompt = build_context_aware_prompt(chat_text, current_date)
    
    client_kwargs = {
        "api_key": api_key,
        "timeout": timeout
    }
    
    if api_base:
        client_kwargs["base_url"] = api_base
    
    try:
        client = openai.OpenAI(**client_kwargs)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的上下文感知任务提取助手。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.0
        )
        
        if not response.choices:
            raise LLMClientError("No choices in LLM response")
        
        content = response.choices[0].message.content
        if not content:
            raise LLMClientError("Empty content in LLM response")
        
        return content.strip()
    
    except openai.APITimeoutError as e:
        raise LLMClientError(f"LLM API timeout: {e}") from e
    except openai.APIConnectionError as e:
        raise LLMClientError(f"LLM API connection error: {e}") from e
    except openai.AuthenticationError as e:
        raise LLMClientError(f"LLM API authentication error: {e}") from e
    except openai.APIError as e:
        raise LLMClientError(f"LLM API error: {e}") from e
    except Exception as e:
        raise LLMClientError(f"Unexpected error calling LLM: {e}") from e


def call_llm_for_group_chat_summary(
    chat_text: str,
    api_base: str,
    api_key: str,
    model: str,
    timeout: int = 30
) -> str:
    """从群聊历史中生成总结和提取任务。

    该函数使用 build_group_chat_summary_prompt 构建提示词，
    引导 LLM 生成完整的群聊总结和任务提取。

    Args:
        chat_text: 群聊历史文本，不能为空字符串
        api_base: API 基础 URL
        api_key: API 密钥
        model: 模型名称
        timeout: 请求超时时间（秒），默认为 30

    Returns:
        LLM 返回的结果字符串（JSON 格式，包含 summary 和 tasks）

    Raises:
        LLMClientError: 当输入无效、API 调用失败或响应格式不正确时
        TypeError: 当 chat_text 类型不正确时
    """
    if not chat_text:
        raise LLMClientError("chat_text cannot be empty")
    
    if not isinstance(chat_text, str):
        raise TypeError(f"chat_text must be a string, got {type(chat_text).__name__}")
    
    if not api_key:
        raise LLMClientError("api_key cannot be empty")
    
    if not model:
        raise LLMClientError("model cannot be empty")
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    prompt = build_group_chat_summary_prompt(chat_text, current_date)
    
    client_kwargs = {
        "api_key": api_key,
        "timeout": timeout
    }
    
    if api_base:
        client_kwargs["base_url"] = api_base
    
    try:
        client = openai.OpenAI(**client_kwargs)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的群聊总结和任务提取助手。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.0
        )
        
        if not response.choices:
            raise LLMClientError("No choices in LLM response")
        
        content = response.choices[0].message.content
        if not content:
            raise LLMClientError("Empty content in LLM response")
        
        return content.strip()
    
    except openai.APITimeoutError as e:
        raise LLMClientError(f"LLM API timeout: {e}") from e
    except openai.APIConnectionError as e:
        raise LLMClientError(f"LLM API connection error: {e}") from e
    except openai.AuthenticationError as e:
        raise LLMClientError(f"LLM API authentication error: {e}") from e
    except openai.APIError as e:
        raise LLMClientError(f"LLM API error: {e}") from e
    except Exception as e:
        raise LLMClientError(f"Unexpected error calling LLM: {e}") from e

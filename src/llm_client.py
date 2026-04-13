from typing import Optional
from datetime import datetime
import openai
from src.config import LLMConfig, get_llm_config
from src.prompt import build_task_extraction_prompt, build_context_aware_prompt


class LLMClientError(Exception):
    pass


def call_llm_for_task_extraction(
    chat_text: str,
    config: Optional[LLMConfig] = None
) -> str:
    if config is None:
        config = get_llm_config()
    
    if not chat_text:
        raise LLMClientError("chat_text cannot be empty")
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    prompt = build_task_extraction_prompt(chat_text, current_date)
    
    client_kwargs = {
        "api_key": config.api_key,
        "timeout": config.timeout
    }
    
    if config.base_url:
        client_kwargs["base_url"] = config.base_url
    
    try:
        client = openai.OpenAI(**client_kwargs)
        
        response = client.chat.completions.create(
            model=config.model,
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
    config: Optional[LLMConfig] = None
) -> str:
    """从聊天文本中进行上下文感知的任务提取。
    
    该函数使用 build_context_aware_prompt 构建提示词，
    引导 LLM 理解对话上下文、识别指代关系并提取任务。
    
    Args:
        chat_text: 聊天文本内容，不能为空字符串
        config: LLM 配置对象，如不提供则使用默认配置
    
    Returns:
        LLM 返回的任务提取结果字符串（JSON 格式）
    
    Raises:
        LLMClientError: 当输入无效、API 调用失败或响应格式不正确时
        TypeError: 当 chat_text 或 config 类型不正确时
    """
    if config is None:
        config = get_llm_config()
    
    if not chat_text:
        raise LLMClientError("chat_text cannot be empty")
    
    if not isinstance(chat_text, str):
        raise TypeError(f"chat_text must be a string, got {type(chat_text).__name__}")
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    prompt = build_context_aware_prompt(chat_text, current_date)
    
    client_kwargs = {
        "api_key": config.api_key,
        "timeout": config.timeout
    }
    
    if config.base_url:
        client_kwargs["base_url"] = config.base_url
    
    try:
        client = openai.OpenAI(**client_kwargs)
        
        response = client.chat.completions.create(
            model=config.model,
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

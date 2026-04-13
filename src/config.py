import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMConfig:
    api_key: str
    base_url: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    timeout: int = 30


def get_llm_config() -> LLMConfig:
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        raise ValueError("LLM_API_KEY environment variable is required")
    
    base_url = os.environ.get("LLM_BASE_URL")
    model = os.environ.get("LLM_MODEL", "gpt-3.5-turbo")
    
    timeout_str = os.environ.get("LLM_TIMEOUT", "30")
    try:
        timeout = int(timeout_str)
    except ValueError:
        timeout = 30
    
    return LLMConfig(
        api_key=api_key,
        base_url=base_url,
        model=model,
        timeout=timeout
    )

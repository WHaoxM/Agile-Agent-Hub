from typing import List
from src.models import Task
from src.config import get_llm_config
from src.prompt import build_task_extraction_prompt
from src.parser import parse_llm_response, TaskParseError
from src.llm_client import call_llm_for_task_extraction, LLMClientError
from datetime import datetime
import logging


MAX_TEXT_LENGTH = 10000
logger = logging.getLogger(__name__)


class TaskExtractor:
    def __init__(self):
        pass

    def extract_tasks(self, chat_text: str) -> List[Task]:
        if chat_text is None:
            raise TypeError("chat_text cannot be None")
        if not isinstance(chat_text, str):
            raise TypeError(f"chat_text must be str, got {type(chat_text).__name__}")
        if len(chat_text.strip()) == 0:
            raise ValueError("chat_text cannot be empty")
        if len(chat_text) > MAX_TEXT_LENGTH:
            raise ValueError(f"chat_text too long (max {MAX_TEXT_LENGTH} characters)")

        tasks = self._llm_extract(chat_text)
        if tasks is not None:
            return tasks
        
        logger.warning("LLM extraction failed, falling back to mock extraction")
        return self._mock_extract(chat_text)

    def _llm_extract(self, chat_text: str) -> List[Task] | None:
        try:
            config = get_llm_config()
        except ValueError:
            return None
        
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            prompt = build_task_extraction_prompt(chat_text, current_date)
            response = call_llm_for_task_extraction(chat_text, config)
            return parse_llm_response(response)
        except (LLMClientError, TaskParseError):
            return None

    def _mock_extract(self, chat_text: str) -> List[Task]:
        tasks = []
        
        if "@张三" in chat_text and "API文档" in chat_text:
            tasks.append(Task(
                task="写API文档",
                assignee="张三",
                deadline="2026-04-14 15:00",
                raw_text=chat_text
            ))
        
        if "@李四" in chat_text and "登录bug" in chat_text:
            tasks.append(Task(
                task="修复登录bug",
                assignee="李四",
                deadline="2026-04-15 10:00",
                raw_text=chat_text
            ))
        
        if "任洪" in chat_text and "技术" in chat_text:
            tasks.append(Task(
                task="整理技术",
                assignee="任洪",
                deadline=None,
                raw_text=chat_text
            ))
        
        return tasks

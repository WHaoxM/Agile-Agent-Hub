import json
from typing import List, Any, Dict
from src.models import Task


class TaskParseError(Exception):
    pass


def parse_llm_response(response: str) -> List[Task]:
    if response is None:
        raise TaskParseError("Response cannot be None")
    if not isinstance(response, str):
        raise TaskParseError(f"Response must be str, got {type(response).__name__}")
    
    response = response.strip()
    if not response:
        raise TaskParseError("Response cannot be empty")
    
    try:
        data = json.loads(response)
    except json.JSONDecodeError as e:
        raise TaskParseError(f"Invalid JSON: {e}") from e
    
    if not isinstance(data, list):
        raise TaskParseError(f"Response must be a list, got {type(data).__name__}")
    
    tasks = []
    for index, item in enumerate(data):
        task = _parse_task_item(item, index)
        tasks.append(task)
    
    return tasks


def _parse_task_item(item: Any, index: int) -> Task:
    if not isinstance(item, dict):
        raise TaskParseError(f"Item {index} must be a dict, got {type(item).__name__}")
    
    task_field = item.get("task")
    if not task_field:
        raise TaskParseError(f"Item {index} missing required 'task' field")
    if not isinstance(task_field, str):
        raise TaskParseError(f"Item {index} 'task' must be str, got {type(task_field).__name__}")
    
    assignee = item.get("assignee")
    if assignee is not None and not isinstance(assignee, str):
        raise TaskParseError(f"Item {index} 'assignee' must be str or null, got {type(assignee).__name__}")
    
    deadline = item.get("deadline")
    if deadline is not None and not isinstance(deadline, str):
        raise TaskParseError(f"Item {index} 'deadline' must be str or null, got {type(deadline).__name__}")
    
    raw_text = item.get("raw_text")
    if not raw_text:
        raise TaskParseError(f"Item {index} missing required 'raw_text' field")
    if not isinstance(raw_text, str):
        raise TaskParseError(f"Item {index} 'raw_text' must be str, got {type(raw_text).__name__}")
    
    return Task(
        task=task_field,
        assignee=assignee,
        deadline=deadline,
        raw_text=raw_text
    )

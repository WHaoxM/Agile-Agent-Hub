import json
from typing import List
from src.models import Task


def tasks_to_json(tasks: List[Task]) -> str:
    task_dicts = [task.to_dict() for task in tasks]
    return json.dumps(task_dicts, ensure_ascii=False, indent=2)


def tasks_to_markdown(tasks: List[Task]) -> str:
    if not tasks:
        return "暂无任务"
    
    lines = []
    lines.append("# 任务清单\n")
    lines.append("| 任务 | 负责人 | 截止时间 | 原始文本 |")
    lines.append("|------|--------|----------|----------|")
    
    for task in tasks:
        task_desc = task.task or "-"
        assignee = task.assignee or "-"
        deadline = task.deadline or "-"
        raw_text = task.raw_text or "-"
        lines.append(f"| {task_desc} | {assignee} | {deadline} | {raw_text} |")
    
    return "\n".join(lines)

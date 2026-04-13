from dataclasses import dataclass
from typing import List
from src.models import Task
from src.extractor import TaskExtractor
from src.output import tasks_to_json, tasks_to_markdown


@dataclass
class PipelineOutput:
    json_output: str
    markdown_output: str
    tasks: List[Task]


class TaskPipeline:
    def __init__(self):
        self.extractor = TaskExtractor()

    def process_chat_text(self, chat_text: str) -> PipelineOutput:
        if chat_text is None:
            raise TypeError("chat_text cannot be None")
        if not isinstance(chat_text, str):
            raise TypeError(f"chat_text must be str, got {type(chat_text).__name__}")

        tasks = self.extractor.extract_tasks(chat_text)
        json_output = tasks_to_json(tasks)
        markdown_output = tasks_to_markdown(tasks)

        return PipelineOutput(
            json_output=json_output,
            markdown_output=markdown_output,
            tasks=tasks
        )

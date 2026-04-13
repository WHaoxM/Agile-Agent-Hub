import json
from src.models import Task


def test_task_creation():
    task = Task(
        task="写API文档",
        assignee="张三",
        deadline="2026-04-14 15:00",
        raw_text="@张三 明天下午3点前把API文档写好"
    )
    assert task.task == "写API文档"
    assert task.assignee == "张三"
    assert task.deadline == "2026-04-14 15:00"
    assert task.raw_text == "@张三 明天下午3点前把API文档写好"


def test_task_to_dict():
    task = Task(
        task="写API文档",
        assignee="张三",
        deadline="2026-04-14 15:00"
    )
    task_dict = task.to_dict()
    assert task_dict["task"] == "写API文档"
    assert task_dict["assignee"] == "张三"
    assert task_dict["deadline"] == "2026-04-14 15:00"


def test_task_to_json():
    task = Task(
        task="写API文档",
        assignee="张三",
        deadline="2026-04-14 15:00"
    )
    task_json = task.to_json()
    parsed = json.loads(task_json)
    assert parsed["task"] == "写API文档"
    assert parsed["assignee"] == "张三"
    assert parsed["deadline"] == "2026-04-14 15:00"


def test_task_with_optional_fields():
    task = Task(task="写API文档")
    assert task.task == "写API文档"
    assert task.assignee is None
    assert task.deadline is None
    assert task.raw_text is None

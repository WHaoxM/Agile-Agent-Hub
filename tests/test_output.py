import json
from src.models import Task
from src.output import tasks_to_json, tasks_to_markdown


def test_tasks_to_json_happy_path():
    tasks = [
        Task(
            task="写API文档",
            assignee="张三",
            deadline="2026-04-14 15:00",
            raw_text="@张三 明天下午3点前把API文档写好"
        ),
        Task(
            task="修复登录bug",
            assignee="李四",
            deadline="2026-04-15 10:00"
        )
    ]
    json_str = tasks_to_json(tasks)
    parsed = json.loads(json_str)
    assert len(parsed) == 2
    assert parsed[0]["task"] == "写API文档"
    assert parsed[0]["assignee"] == "张三"
    assert parsed[1]["task"] == "修复登录bug"
    assert parsed[1]["assignee"] == "李四"


def test_tasks_to_json_empty_list():
    tasks = []
    json_str = tasks_to_json(tasks)
    parsed = json.loads(json_str)
    assert parsed == []


def test_tasks_to_markdown_happy_path():
    tasks = [
        Task(
            task="写API文档",
            assignee="张三",
            deadline="2026-04-14 15:00",
            raw_text="@张三 明天下午3点前把API文档写好"
        )
    ]
    markdown = tasks_to_markdown(tasks)
    assert "# 任务清单" in markdown
    assert "写API文档" in markdown
    assert "张三" in markdown
    assert "2026-04-14 15:00" in markdown


def test_tasks_to_markdown_empty_list():
    tasks = []
    markdown = tasks_to_markdown(tasks)
    assert markdown == "暂无任务"


def test_tasks_to_markdown_with_missing_fields():
    tasks = [
        Task(task="写代码"),
        Task(task="测试", assignee="王五")
    ]
    markdown = tasks_to_markdown(tasks)
    assert "写代码" in markdown
    assert "测试" in markdown
    assert "王五" in markdown

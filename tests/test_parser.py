import pytest
from src.parser import parse_llm_response, TaskParseError
from src.models import Task


def test_parse_valid_response():
    response = '''[
      {
        "task": "写API文档",
        "assignee": "张三",
        "deadline": "2026-04-14 15:00",
        "raw_text": "@张三 明天下午3点前把API文档写好"
      }
    ]'''
    
    tasks = parse_llm_response(response)
    assert len(tasks) == 1
    assert tasks[0].task == "写API文档"
    assert tasks[0].assignee == "张三"
    assert tasks[0].deadline == "2026-04-14 15:00"
    assert tasks[0].raw_text == "@张三 明天下午3点前把API文档写好"


def test_parse_multiple_tasks():
    response = '''[
      {
        "task": "写API文档",
        "assignee": "张三",
        "deadline": "2026-04-14 15:00",
        "raw_text": "@张三 明天下午3点前把API文档写好"
      },
      {
        "task": "修复登录bug",
        "assignee": "李四",
        "deadline": "2026-04-15 10:00",
        "raw_text": "@李四 后天上午10点前修复登录bug"
      }
    ]'''
    
    tasks = parse_llm_response(response)
    assert len(tasks) == 2
    task_descriptions = [t.task for t in tasks]
    assert "写API文档" in task_descriptions
    assert "修复登录bug" in task_descriptions


def test_parse_null_assignee_and_deadline():
    response = '''[
      {
        "task": "整理技术",
        "assignee": null,
        "deadline": null,
        "raw_text": "@任洪 你整理好技术了吗"
      }
    ]'''
    
    tasks = parse_llm_response(response)
    assert len(tasks) == 1
    assert tasks[0].task == "整理技术"
    assert tasks[0].assignee is None
    assert tasks[0].deadline is None
    assert tasks[0].raw_text == "@任洪 你整理好技术了吗"


def test_parse_none_response():
    with pytest.raises(TaskParseError, match="Response cannot be None"):
        parse_llm_response(None)


def test_parse_non_string_response():
    with pytest.raises(TaskParseError, match="Response must be str"):
        parse_llm_response(123)


def test_parse_empty_response():
    with pytest.raises(TaskParseError, match="Response cannot be empty"):
        parse_llm_response("")


def test_parse_whitespace_only_response():
    with pytest.raises(TaskParseError, match="Response cannot be empty"):
        parse_llm_response("   \n  ")


def test_parse_invalid_json():
    with pytest.raises(TaskParseError, match="Invalid JSON"):
        parse_llm_response("{invalid json}")


def test_parse_json_not_list():
    with pytest.raises(TaskParseError, match="Response must be a list"):
        parse_llm_response('{"task": "写代码"}')


def test_parse_item_not_dict():
    with pytest.raises(TaskParseError, match="Item 0 must be a dict"):
        parse_llm_response('["not a dict"]')


def test_parse_missing_task_field():
    response = '''[
      {
        "assignee": "张三",
        "raw_text": "test"
      }
    ]'''
    with pytest.raises(TaskParseError, match="Item 0 missing required 'task' field"):
        parse_llm_response(response)


def test_parse_task_not_string():
    response = '''[
      {
        "task": 123,
        "raw_text": "test"
      }
    ]'''
    with pytest.raises(TaskParseError, match="Item 0 'task' must be str"):
        parse_llm_response(response)


def test_parse_missing_raw_text_field():
    response = '''[
      {
        "task": "写代码",
        "assignee": "张三"
      }
    ]'''
    with pytest.raises(TaskParseError, match="Item 0 missing required 'raw_text' field"):
        parse_llm_response(response)


def test_parse_raw_text_not_string():
    response = '''[
      {
        "task": "写代码",
        "raw_text": 123
      }
    ]'''
    with pytest.raises(TaskParseError, match="Item 0 'raw_text' must be str"):
        parse_llm_response(response)


def test_parse_assignee_not_string_or_null():
    response = '''[
      {
        "task": "写代码",
        "assignee": 123,
        "raw_text": "test"
      }
    ]'''
    with pytest.raises(TaskParseError, match="Item 0 'assignee' must be str or null"):
        parse_llm_response(response)


def test_parse_deadline_not_string_or_null():
    response = '''[
      {
        "task": "写代码",
        "deadline": 123,
        "raw_text": "test"
      }
    ]'''
    with pytest.raises(TaskParseError, match="Item 0 'deadline' must be str or null"):
        parse_llm_response(response)


def test_parse_empty_list():
    tasks = parse_llm_response("[]")
    assert len(tasks) == 0

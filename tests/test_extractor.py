import pytest
from src.extractor import TaskExtractor, MAX_TEXT_LENGTH
from src.models import Task
from src.config import LLMConfig
from src.llm_client import LLMClientError
from src.parser import TaskParseError


def test_extract_tasks_happy_path_zhangsan():
    extractor = TaskExtractor()
    chat_text = "@张三 明天下午3点前把API文档写好"
    tasks = extractor.extract_tasks(chat_text)
    assert len(tasks) == 1
    assert tasks[0].task == "写API文档"
    assert tasks[0].assignee == "张三"
    assert tasks[0].deadline == "2026-04-14 15:00"
    assert tasks[0].raw_text == chat_text


def test_extract_tasks_happy_path_lisi():
    extractor = TaskExtractor()
    chat_text = "@李四 后天上午10点前修复登录bug"
    tasks = extractor.extract_tasks(chat_text)
    assert len(tasks) == 1
    assert tasks[0].task == "修复登录bug"
    assert tasks[0].assignee == "李四"
    assert tasks[0].deadline == "2026-04-15 10:00"


def test_extract_tasks_renhong():
    extractor = TaskExtractor()
    chat_text = "@任洪 你整理好技术了吗"
    tasks = extractor.extract_tasks(chat_text)
    assert len(tasks) == 1
    assert tasks[0].task == "整理技术"
    assert tasks[0].assignee == "任洪"
    assert tasks[0].deadline is None


def test_extract_tasks_none_input():
    extractor = TaskExtractor()
    with pytest.raises(TypeError, match="chat_text cannot be None"):
        extractor.extract_tasks(None)


def test_extract_tasks_non_string_input():
    extractor = TaskExtractor()
    with pytest.raises(TypeError, match="chat_text must be str"):
        extractor.extract_tasks(123)


def test_extract_tasks_empty_string():
    extractor = TaskExtractor()
    with pytest.raises(ValueError, match="chat_text cannot be empty"):
        extractor.extract_tasks("")


def test_extract_tasks_whitespace_only():
    extractor = TaskExtractor()
    with pytest.raises(ValueError, match="chat_text cannot be empty"):
        extractor.extract_tasks("   \n  ")


def test_extract_tasks_too_long():
    extractor = TaskExtractor()
    long_text = "x" * (MAX_TEXT_LENGTH + 1)
    with pytest.raises(ValueError, match="chat_text too long"):
        extractor.extract_tasks(long_text)


def test_extract_tasks_no_tasks_found():
    extractor = TaskExtractor()
    chat_text = "今天天气真好"
    tasks = extractor.extract_tasks(chat_text)
    assert len(tasks) == 0


def test_extract_tasks_multiple_tasks():
    extractor = TaskExtractor()
    chat_text = "@张三 写API文档 @李四 修复登录bug"
    tasks = extractor.extract_tasks(chat_text)
    assert len(tasks) == 2
    task_descriptions = [t.task for t in tasks]
    assert "写API文档" in task_descriptions
    assert "修复登录bug" in task_descriptions


def test_extract_tasks_llm_success(mocker):
    mocker.patch("src.extractor.get_llm_config").return_value = LLMConfig(
        api_key="test_key"
    )
    mocker.patch("src.extractor.call_llm_for_task_extraction").return_value = "mock response"
    mock_tasks = [
        Task(task="测试任务", assignee="测试人", deadline="2026-04-14 12:00", raw_text="测试文本")
    ]
    mocker.patch("src.extractor.parse_llm_response").return_value = mock_tasks
    
    extractor = TaskExtractor()
    chat_text = "@测试人 测试任务"
    tasks = extractor.extract_tasks(chat_text)
    
    assert len(tasks) == 1
    assert tasks[0].task == "测试任务"


def test_extract_tasks_llm_no_api_key(mocker):
    mocker.patch("src.extractor.get_llm_config").side_effect = ValueError("No API key")
    mock_warning = mocker.patch("src.extractor.logger.warning")
    
    extractor = TaskExtractor()
    chat_text = "@张三 明天下午3点前把API文档写好"
    tasks = extractor.extract_tasks(chat_text)
    
    assert len(tasks) == 1
    assert tasks[0].task == "写API文档"
    mock_warning.assert_called_once_with("LLM extraction failed, falling back to mock extraction")


def test_extract_tasks_llm_client_error(mocker):
    mocker.patch("src.extractor.get_llm_config").return_value = LLMConfig(
        api_key="test_key"
    )
    mocker.patch("src.extractor.call_llm_for_task_extraction").side_effect = LLMClientError("Client error")
    mock_warning = mocker.patch("src.extractor.logger.warning")
    
    extractor = TaskExtractor()
    chat_text = "@张三 明天下午3点前把API文档写好"
    tasks = extractor.extract_tasks(chat_text)
    
    assert len(tasks) == 1
    assert tasks[0].task == "写API文档"
    mock_warning.assert_called_once_with("LLM extraction failed, falling back to mock extraction")


def test_extract_tasks_llm_parse_error(mocker):
    mocker.patch("src.extractor.get_llm_config").return_value = LLMConfig(
        api_key="test_key"
    )
    mocker.patch("src.extractor.call_llm_for_task_extraction").return_value = "invalid json"
    mocker.patch("src.extractor.parse_llm_response").side_effect = TaskParseError("Parse error")
    mock_warning = mocker.patch("src.extractor.logger.warning")
    
    extractor = TaskExtractor()
    chat_text = "@张三 明天下午3点前把API文档写好"
    tasks = extractor.extract_tasks(chat_text)
    
    assert len(tasks) == 1
    assert tasks[0].task == "写API文档"
    mock_warning.assert_called_once_with("LLM extraction failed, falling back to mock extraction")

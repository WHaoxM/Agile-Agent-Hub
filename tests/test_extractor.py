import pytest
import os
from src.extractor import TaskExtractor, MAX_TEXT_LENGTH
from src.models import Task
from src.config import LLMConfig
from src.llm_client import LLMClientError
from src.parser import TaskParseError


def test_extract_tasks_happy_path_zhangsan():
    extractor = TaskExtractor()
    chat_text = "@张三 明天下午3点前把API文档写好"
    
    api_key = os.environ.pop("LLM_API_KEY", None)
    try:
        tasks = extractor.extract_tasks(chat_text)
        assert len(tasks) == 1
        assert tasks[0].task == "写API文档"
        assert tasks[0].assignee == "张三"
        assert tasks[0].deadline == "2026-04-14 15:00"
        assert tasks[0].raw_text == chat_text
    finally:
        if api_key is not None:
            os.environ["LLM_API_KEY"] = api_key


def test_extract_tasks_happy_path_lisi():
    extractor = TaskExtractor()
    chat_text = "@李四 后天上午10点前修复登录bug"
    
    api_key = os.environ.pop("LLM_API_KEY", None)
    try:
        tasks = extractor.extract_tasks(chat_text)
        assert len(tasks) == 1
        assert tasks[0].task == "修复登录bug"
        assert tasks[0].assignee == "李四"
        assert tasks[0].deadline == "2026-04-15 10:00"
    finally:
        if api_key is not None:
            os.environ["LLM_API_KEY"] = api_key


def test_extract_tasks_renhong():
    extractor = TaskExtractor()
    chat_text = "@任洪 你整理好技术了吗"
    
    api_key = os.environ.pop("LLM_API_KEY", None)
    try:
        tasks = extractor.extract_tasks(chat_text)
        assert len(tasks) == 1
        assert tasks[0].task == "整理技术"
        assert tasks[0].assignee == "任洪"
        assert tasks[0].deadline is None
    finally:
        if api_key is not None:
            os.environ["LLM_API_KEY"] = api_key


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
    
    api_key = os.environ.pop("LLM_API_KEY", None)
    try:
        tasks = extractor.extract_tasks(chat_text)
        assert len(tasks) == 0
    finally:
        if api_key is not None:
            os.environ["LLM_API_KEY"] = api_key


def test_extract_tasks_multiple_tasks():
    extractor = TaskExtractor()
    chat_text = "@张三 写API文档 @李四 修复登录bug"
    
    api_key = os.environ.pop("LLM_API_KEY", None)
    try:
        tasks = extractor.extract_tasks(chat_text)
        assert len(tasks) == 2
        task_descriptions = [t.task for t in tasks]
        assert "写API文档" in task_descriptions
        assert "修复登录bug" in task_descriptions
    finally:
        if api_key is not None:
            os.environ["LLM_API_KEY"] = api_key


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
    assert mock_warning.call_count == 2
    mock_warning.assert_any_call("Context-aware extraction failed, falling back to LLM extraction")
    mock_warning.assert_any_call("LLM extraction failed, falling back to mock extraction")


def test_extract_tasks_llm_client_error(mocker):
    mocker.patch("src.extractor.get_llm_config").return_value = LLMConfig(
        api_key="test_key"
    )
    mocker.patch("src.extractor.call_llm_for_context_aware_extraction").side_effect = LLMClientError("Client error")
    mocker.patch("src.extractor.call_llm_for_task_extraction").side_effect = LLMClientError("Client error")
    mock_warning = mocker.patch("src.extractor.logger.warning")
    
    extractor = TaskExtractor()
    chat_text = "@张三 明天下午3点前把API文档写好"
    tasks = extractor.extract_tasks(chat_text)
    
    assert len(tasks) == 1
    assert tasks[0].task == "写API文档"
    assert mock_warning.call_count == 2
    mock_warning.assert_any_call("Context-aware extraction failed, falling back to LLM extraction")
    mock_warning.assert_any_call("LLM extraction failed, falling back to mock extraction")


def test_extract_tasks_llm_parse_error(mocker):
    mocker.patch("src.extractor.get_llm_config").return_value = LLMConfig(
        api_key="test_key"
    )
    mocker.patch("src.extractor.call_llm_for_context_aware_extraction").return_value = "invalid json"
    mocker.patch("src.extractor.call_llm_for_task_extraction").return_value = "invalid json"
    mocker.patch("src.extractor.parse_llm_response").side_effect = TaskParseError("Parse error")
    mock_warning = mocker.patch("src.extractor.logger.warning")
    
    extractor = TaskExtractor()
    chat_text = "@张三 明天下午3点前把API文档写好"
    tasks = extractor.extract_tasks(chat_text)
    
    assert len(tasks) == 1
    assert tasks[0].task == "写API文档"
    assert mock_warning.call_count == 2
    mock_warning.assert_any_call("Context-aware extraction failed, falling back to LLM extraction")
    mock_warning.assert_any_call("LLM extraction failed, falling back to mock extraction")


def test_extract_tasks_context_aware_success(mocker):
    mocker.patch("src.extractor.get_llm_config").return_value = LLMConfig(
        api_key="test_key"
    )
    mocker.patch("src.extractor.call_llm_for_context_aware_extraction").return_value = "mock context response"
    mock_tasks = [
        Task(task="上下文感知测试任务", assignee="上下文测试人", deadline="2026-04-14 14:00", raw_text="测试文本")
    ]
    mocker.patch("src.extractor.parse_llm_response").return_value = mock_tasks
    mock_call_task = mocker.patch("src.extractor.call_llm_for_task_extraction")
    
    extractor = TaskExtractor()
    chat_text = "@上下文测试人 上下文感知测试任务"
    tasks = extractor.extract_tasks(chat_text)
    
    assert len(tasks) == 1
    assert tasks[0].task == "上下文感知测试任务"
    assert tasks[0].assignee == "上下文测试人"
    assert mock_call_task.call_count == 0


def test_extract_tasks_long_text(mocker):
    mocker.patch("src.extractor.get_llm_config").return_value = LLMConfig(
        api_key="test_key"
    )
    mocker.patch("src.extractor.call_llm_for_context_aware_extraction").return_value = "mock long text response"
    mock_tasks = [
        Task(task="长文本任务", assignee="长文本人", deadline="2026-04-14 16:00", raw_text="长文本测试")
    ]
    mocker.patch("src.extractor.parse_llm_response").return_value = mock_tasks
    
    extractor = TaskExtractor()
    long_text = "@长文本人 长文本任务 " + "x" * (MAX_TEXT_LENGTH - 20)
    tasks = extractor.extract_tasks(long_text)
    
    assert len(tasks) == 1
    assert tasks[0].task == "长文本任务"
    assert tasks[0].assignee == "长文本人"


def test_extract_tasks_context_fallback(mocker):
    mocker.patch("src.extractor.get_llm_config").return_value = LLMConfig(
        api_key="test_key"
    )
    mocker.patch("src.extractor.call_llm_for_context_aware_extraction").side_effect = LLMClientError("Context error")
    mocker.patch("src.extractor.call_llm_for_task_extraction").return_value = "mock fallback response"
    mock_tasks = [
        Task(task="降级测试任务", assignee="降级测试人", deadline="2026-04-14 17:00", raw_text="降级测试")
    ]
    mocker.patch("src.extractor.parse_llm_response").return_value = mock_tasks
    mock_warning = mocker.patch("src.extractor.logger.warning")
    
    extractor = TaskExtractor()
    chat_text = "@降级测试人 降级测试任务"
    tasks = extractor.extract_tasks(chat_text)
    
    assert len(tasks) == 1
    assert tasks[0].task == "降级测试任务"
    assert tasks[0].assignee == "降级测试人"
    assert mock_warning.call_count == 1
    mock_warning.assert_any_call("Context-aware extraction failed, falling back to LLM extraction")

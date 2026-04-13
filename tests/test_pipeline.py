import pytest
import json
import os
from src.pipeline import TaskPipeline, PipelineOutput


def test_pipeline_process_chat_text_happy_path():
    pipeline = TaskPipeline()
    chat_text = "@张三 明天下午3点前把API文档写好"
    
    api_key = os.environ.pop("LLM_API_KEY", None)
    try:
        output = pipeline.process_chat_text(chat_text)
        
        assert isinstance(output, PipelineOutput)
        assert isinstance(output.json_output, str)
        assert isinstance(output.markdown_output, str)
        assert len(output.tasks) == 1
        assert output.tasks[0].task == "写API文档"
        assert output.tasks[0].assignee == "张三"
        
        parsed_json = json.loads(output.json_output)
        assert len(parsed_json) == 1
        assert parsed_json[0]["task"] == "写API文档"
        
        assert "# 任务清单" in output.markdown_output
        assert "写API文档" in output.markdown_output
    finally:
        if api_key is not None:
            os.environ["LLM_API_KEY"] = api_key


def test_pipeline_process_chat_text_multiple_tasks():
    pipeline = TaskPipeline()
    chat_text = "@张三 写API文档 @李四 修复登录bug"
    
    api_key = os.environ.pop("LLM_API_KEY", None)
    try:
        output = pipeline.process_chat_text(chat_text)
        
        assert len(output.tasks) == 2
        task_descriptions = [t.task for t in output.tasks]
        assert "写API文档" in task_descriptions
        assert "修复登录bug" in task_descriptions
    finally:
        if api_key is not None:
            os.environ["LLM_API_KEY"] = api_key


def test_pipeline_process_chat_text_none_input():
    pipeline = TaskPipeline()
    with pytest.raises(TypeError, match="chat_text cannot be None"):
        pipeline.process_chat_text(None)


def test_pipeline_process_chat_text_non_string_input():
    pipeline = TaskPipeline()
    with pytest.raises(TypeError, match="chat_text must be str"):
        pipeline.process_chat_text(123)


def test_pipeline_process_chat_text_empty_string():
    pipeline = TaskPipeline()
    with pytest.raises(ValueError, match="chat_text cannot be empty"):
        pipeline.process_chat_text("")


def test_pipeline_process_chat_text_no_tasks():
    pipeline = TaskPipeline()
    chat_text = "今天天气真好"
    
    api_key = os.environ.pop("LLM_API_KEY", None)
    try:
        output = pipeline.process_chat_text(chat_text)
        
        assert len(output.tasks) == 0
        assert output.json_output == "[]"
        assert output.markdown_output == "暂无任务"
    finally:
        if api_key is not None:
            os.environ["LLM_API_KEY"] = api_key


def test_pipeline_output_dataclass():
    pipeline = TaskPipeline()
    chat_text = "@任洪 你整理好技术了吗"
    
    api_key = os.environ.pop("LLM_API_KEY", None)
    try:
        output = pipeline.process_chat_text(chat_text)
        
        assert hasattr(output, "json_output")
        assert hasattr(output, "markdown_output")
        assert hasattr(output, "tasks")
    finally:
        if api_key is not None:
            os.environ["LLM_API_KEY"] = api_key

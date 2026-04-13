from src.prompt import build_task_extraction_prompt, TASK_EXTRACTION_PROMPT


def test_prompt_contains_required_instructions():
    assert "JSON 数组" in TASK_EXTRACTION_PROMPT
    assert "task" in TASK_EXTRACTION_PROMPT
    assert "assignee" in TASK_EXTRACTION_PROMPT
    assert "deadline" in TASK_EXTRACTION_PROMPT
    assert "raw_text" in TASK_EXTRACTION_PROMPT


def test_build_prompt_inserts_chat_text():
    chat_text = "@王五 下周五前完成项目报告"
    current_date = "2026-04-13"
    prompt = build_task_extraction_prompt(chat_text, current_date)
    
    assert chat_text in prompt
    assert current_date in prompt


def test_prompt_contains_example():
    assert "@张三 明天下午3点前把API文档写好" in TASK_EXTRACTION_PROMPT
    assert "写API文档" in TASK_EXTRACTION_PROMPT
    assert "修复登录bug" in TASK_EXTRACTION_PROMPT


def test_prompt_contains_json_format_requirement():
    assert "只返回 JSON" in TASK_EXTRACTION_PROMPT
    assert "不要包含任何其他文本" in TASK_EXTRACTION_PROMPT


def test_build_prompt_with_special_chars():
    chat_text = "@赵六 | 测试任务 & 包含特殊字符"
    current_date = "2026-04-13"
    prompt = build_task_extraction_prompt(chat_text, current_date)
    
    assert chat_text in prompt

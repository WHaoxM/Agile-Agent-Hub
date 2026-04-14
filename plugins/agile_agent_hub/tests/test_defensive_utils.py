"""
防御性工具模块测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from defensive_utils import (
    safe_format_group_messages,
    validate_date_string,
    safe_make_dirs,
    safe_filename,
    safe_json_loads,
    safe_json_dumps,
    validate_llm_config,
    validate_schedule_time,
    validate_monitored_groups
)
from datetime import datetime


def test_safe_format_group_messages():
    """测试安全的消息格式化功能"""
    print("=" * 60)
    print("测试 1: safe_format_group_messages")
    print("=" * 60)
    
    # 正常情况
    test_messages = [
        {
            "sender_name": "用户1",
            "content": "第一条消息",
            "timestamp": datetime.now().timestamp()
        },
        {
            "sender_name": "用户2",
            "content": "第二条消息",
            "timestamp": datetime.now().timestamp()
        }
    ]
    
    result = safe_format_group_messages(test_messages)
    print(f"正常输入: {test_messages}")
    print(f"输出: {result[:100]}...")
    assert "用户1" in result
    assert "第一条消息" in result
    print("✓ 正常情况测试通过")
    
    # 边界情况 - 空列表
    result = safe_format_group_messages([])
    print(f"\n空列表输入: []")
    print(f"输出: '{result}'")
    assert result == ""
    print("✓ 空列表测试通过")
    
    # 边界情况 - 不完整的消息对象
    incomplete_messages = [
        {"sender_name": "用户"},
        {"content": "只有内容"},
        {"timestamp": datetime.now().timestamp()}
    ]
    
    result = safe_format_group_messages(incomplete_messages)
    print(f"\n不完整输入: {incomplete_messages}")
    print(f"输出: {result}")
    assert "用户" in result or "只有内容" in result
    print("✓ 不完整输入测试通过")
    
    # 边界情况 - 超长内容
    long_content = "a" * 15000
    long_messages = [{"sender_name": "用户", "content": long_content}]
    
    result = safe_format_group_messages(long_messages)
    print(f"\n超长内容输入 (15000字符)")
    print(f"输出长度: {len(result)}")
    assert len(result) <= 10000  # 应该被截断到 10000 字符以内
    print("✓ 超长内容测试通过")
    
    print("\n✅ safe_format_group_messages 所有测试通过\n")


def test_date_validation():
    """测试日期验证"""
    print("=" * 60)
    print("测试 2: validate_date_string")
    print("=" * 60)
    
    # 正常日期
    valid_dates = ["2024-01-01", "2024-12-31", "2025-02-28"]
    for date in valid_dates:
        is_valid = validate_date_string(date)
        print(f"测试日期 '{date}': {'有效' if is_valid else '无效'}")
        assert is_valid
    
    # 无效日期
    invalid_dates = ["2024/01/01", "2024-13-01", "2024-01-32", "invalid", ""]
    for date in invalid_dates:
        is_valid = validate_date_string(date)
        print(f"测试日期 '{date}': {'有效' if is_valid else '无效'}")
        assert not is_valid
    
    print("\n✅ validate_date_string 所有测试通过\n")


def test_file_operations():
    """测试文件操作工具"""
    print("=" * 60)
    print("测试 3: 文件操作工具")
    print("=" * 60)
    
    # 测试 safe_filename
    test_filenames = [
        ("test.json", "test.json"),
        ("../../etc/passwd", "etc_passwd"),
        ("file with spaces.txt", "file_with_spaces.txt"),
        ("file/with/slashes", "file_with_slashes"),
        ("file\\with\\backslashes", "file_with_backslashes"),
        ("file:with:colons", "file_with_colons"),
        ("file*with*stars", "file_with_stars"),
        ("file?with?question", "file_with_question"),
        ('file"with"quotes', "file_with_quotes"),
        ("file<with>angles", "file_with_angles"),
        ("file|with|pipes", "file_with_pipes"),
    ]
    
    for input_name, expected in test_filenames:
        result = safe_filename(input_name)
        print(f"safe_filename('{input_name}') = '{result}'")
        assert result == expected
    
    print("\n✅ safe_filename 所有测试通过\n")


def test_json_operations():
    """测试 JSON 操作工具"""
    print("=" * 60)
    print("测试 4: JSON 操作工具")
    print("=" * 60)
    
    # 测试 safe_json_loads
    valid_json = '{"key": "value", "number": 42}'
    result = safe_json_loads(valid_json)
    print(f"safe_json_loads('{valid_json}') = {result}")
    assert result == {"key": "value", "number": 42}
    
    # 测试无效 JSON
    invalid_json = '{"key": value, "number": 42}'  # 缺少引号
    result = safe_json_loads(invalid_json, default={})
    print(f"safe_json_loads('{invalid_json}', default={{}}) = {result}")
    assert result == {}
    
    # 测试 safe_json_dumps
    data = {"key": "value", "list": [1, 2, 3]}
    json_str = safe_json_dumps(data)
    print(f"safe_json_dumps({data}) = '{json_str}'")
    assert isinstance(json_str, str)
    assert "key" in json_str
    assert "value" in json_str
    
    print("\n✅ JSON 操作工具所有测试通过\n")


def test_config_validation():
    """测试配置验证"""
    print("=" * 60)
    print("测试 5: 配置验证")
    print("=" * 60)
    
    # 测试 validate_llm_config
    valid_config = {
        "llm_api_base": "https://api.openai.com/v1",
        "llm_api_key": "sk-1234567890abcdef",
        "llm_model": "gpt-4o"
    }
    is_valid, errors = validate_llm_config(valid_config)
    print(f"LLM 配置验证 (有效): {is_valid}, 错误: {errors}")
    assert is_valid
    assert len(errors) == 0
    
    invalid_config = {
        "llm_api_base": "",
        "llm_api_key": "",
        "llm_model": ""
    }
    is_valid, errors = validate_llm_config(invalid_config)
    print(f"LLM 配置验证 (无效): {is_valid}, 错误: {errors}")
    assert not is_valid
    assert len(errors) > 0
    
    # 测试 validate_schedule_time
    valid_times = ["08:00", "12:30", "23:59", "00:00"]
    for time_str in valid_times:
        is_valid = validate_schedule_time(time_str)
        print(f"validate_schedule_time('{time_str}') = {is_valid}")
        assert is_valid
    
    invalid_times = ["25:00", "12:60", "invalid", "8:00", "123:45"]
    for time_str in invalid_times:
        is_valid = validate_schedule_time(time_str)
        print(f"validate_schedule_time('{time_str}') = {is_valid}")
        assert not is_valid
    
    # 测试 validate_monitored_groups
    valid_groups = ["10001", "10002", "123456789"]
    is_valid, errors = validate_monitored_groups(valid_groups)
    print(f"validate_monitored_groups({valid_groups}): {is_valid}, 错误: {errors}")
    assert is_valid
    
    invalid_groups = ["", "  ", "group1", None]
    is_valid, errors = validate_monitored_groups(invalid_groups)
    print(f"validate_monitored_groups({invalid_groups}): {is_valid}, 错误: {errors}")
    assert not is_valid
    
    print("\n✅ 配置验证所有测试通过\n")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("防御性工具模块测试套件")
    print("=" * 60 + "\n")
    
    try:
        test_safe_format_group_messages()
        test_date_validation()
        test_file_operations()
        test_json_operations()
        test_config_validation()
        
        print("=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        return True
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ 测试失败: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)


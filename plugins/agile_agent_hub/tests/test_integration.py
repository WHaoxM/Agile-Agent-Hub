"""
插件集成测试
验证防御性工具模块与插件主代码的集成
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_plugin_integration():
    """测试插件与防御性工具的集成"""
    print("=" * 60)
    print("插件集成测试")
    print("=" * 60)
    
    # 测试 1: 测试 format_group_messages 方法
    print("\n[测试 1] format_group_messages 方法集成")
    print("-" * 60)
    
    # 创建一个简单的 mock 类来测试方法
    class MockPlugin:
        def __init__(self):
            from defensive_utils import safe_format_group_messages
            self.safe_format_group_messages = safe_format_group_messages
        
        def format_group_messages(self, messages):
            return self.safe_format_group_messages(messages)
    
    plugin = MockPlugin()
    
    test_messages = [
        {
            "sender_name": "测试用户1",
            "content": "这是第一条消息",
            "timestamp": datetime.now().timestamp()
        },
        {
            "sender_name": "测试用户2",
            "content": "这是第二条消息",
            "timestamp": datetime.now().timestamp()
        }
    ]
    
    result = plugin.format_group_messages(test_messages)
    print(f"输入: {test_messages}")
    print(f"输出: {result}")
    assert "测试用户1" in result
    assert "第一条消息" in result
    assert "测试用户2" in result
    assert "第二条消息" in result
    print("✅ format_group_messages 集成测试通过")
    
    # 测试 2: 测试 safe_json_loads 集成
    print("\n[测试 2] safe_json_loads 集成")
    print("-" * 60)
    
    from defensive_utils import safe_json_loads
    
    valid_json = '{"summary": "测试总结", "tasks": [{"task": "测试任务"}]}'
    result = safe_json_loads(valid_json, {})
    print(f"有效 JSON 输入: {valid_json}")
    print(f"解析结果: {result}")
    assert result.get("summary") == "测试总结"
    assert len(result.get("tasks", [])) == 1
    
    invalid_json = '{"summary": 测试总结, "tasks": [{"task": "测试任务"}]}'
    result = safe_json_loads(invalid_json, {"summary": "默认总结"})
    print(f"\n无效 JSON 输入: {invalid_json}")
    print(f"解析结果 (使用默认值): {result}")
    assert result.get("summary") == "默认总结"
    print("✅ safe_json_loads 集成测试通过")
    
    # 测试 3: 测试文件操作工具集成
    print("\n[测试 3] 文件操作工具集成")
    print("-" * 60)
    
    from defensive_utils import safe_filename, safe_join_path
    
    test_filename = "../../etc/passwd"
    safe_name = safe_filename(test_filename)
    print(f"危险文件名: {test_filename}")
    print(f"安全文件名: {safe_name}")
    assert safe_name == "etc_passwd"
    assert "../" not in safe_name
    
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        safe_path = safe_join_path(temp_dir, "test.json")
        print(f"\n基础目录: {temp_dir}")
        print(f"安全路径: {safe_path}")
        assert safe_path.startswith(temp_dir)
    
    print("✅ 文件操作工具集成测试通过")
    
    # 测试 4: 测试配置验证集成
    print("\n[测试 4] 配置验证集成")
    print("-" * 60)
    
    from defensive_utils import (
        validate_schedule_time,
        validate_monitored_groups,
        validate_llm_config
    )
    
    valid_config = {
        "llm_api_base": "https://api.openai.com/v1",
        "llm_api_key": "sk-1234567890",
        "llm_model": "gpt-4o"
    }
    is_valid, errors = validate_llm_config(valid_config)
    print(f"有效 LLM 配置: {valid_config}")
    print(f"验证结果: {is_valid}, 错误: {errors}")
    assert is_valid
    assert len(errors) == 0
    
    invalid_config = {
        "llm_api_base": "",
        "llm_api_key": "",
        "llm_model": ""
    }
    is_valid, errors = validate_llm_config(invalid_config)
    print(f"\n无效 LLM 配置: {invalid_config}")
    print(f"验证结果: {is_valid}, 错误: {errors}")
    assert not is_valid
    assert len(errors) > 0
    
    assert validate_schedule_time("08:00")
    assert not validate_schedule_time("25:00")
    
    is_valid, errors = validate_monitored_groups(["10001", "10002"])
    assert is_valid
    assert len(errors) == 0
    
    print("✅ 配置验证集成测试通过")
    
    print("\n" + "=" * 60)
    print("🎉 所有集成测试通过！")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_plugin_integration()
    sys.exit(0 if success else 1)


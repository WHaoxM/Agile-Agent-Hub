"""
Agile Agent Hub 插件测试

规范:
  PL-01: 插件加载成功，on_load 执行
  PL-02: 群消息被正确收集和存储
  PL-03: 配置正确初始化
  PL-04: 定时任务正确注册
  PL-05: 消息格式化功能正常
"""

import pytest
from pathlib import Path
from datetime import datetime

from ncatbot.testing import PluginTestHarness
from ncatbot.testing.factories.qq import group_message


PLUGIN_NAME = "agile_agent_hub"
PLUGINS_DIR = Path(__file__).resolve().parents[1]


# ---- PL-01: 加载 ----

async def test_plugin_loads_successfully():
    """PL-01: agile_agent_hub 插件加载成功"""
    async with PluginTestHarness(
        plugin_names=[PLUGIN_NAME], plugins_dir=PLUGINS_DIR
    ) as h:
        assert PLUGIN_NAME in h.loaded_plugins
        plugin = h.get_plugin(PLUGIN_NAME)
        assert plugin is not None
        assert plugin.name == PLUGIN_NAME


# ---- PL-02: 群消息收集 ----

async def test_group_message_collection():
    """PL-02: 群消息被正确收集和存储"""
    async with PluginTestHarness(
        plugin_names=[PLUGIN_NAME], plugins_dir=PLUGINS_DIR
    ) as h:
        plugin = h.get_plugin(PLUGIN_NAME)
        
        today = datetime.now().strftime("%Y-%m-%d")
        group_id = "10001"
        
        await h.inject(group_message("测试消息", group_id=group_id, user_id="99999", sender_name="测试用户"))
        await h.settle(0.1)
        
        assert "messages" in plugin.data
        assert today in plugin.data["messages"]
        assert group_id in plugin.data["messages"][today]
        assert len(plugin.data["messages"][today][group_id]) == 1
        
        message = plugin.data["messages"][today][group_id][0]
        assert message["sender_name"] == "测试用户"
        assert message["content"] == "测试消息"


async def test_multiple_group_messages():
    """PL-02b: 多条群消息被正确收集"""
    async with PluginTestHarness(
        plugin_names=[PLUGIN_NAME], plugins_dir=PLUGINS_DIR
    ) as h:
        plugin = h.get_plugin(PLUGIN_NAME)
        
        today = datetime.now().strftime("%Y-%m-%d")
        group_id = "10001"
        
        await h.inject(group_message("消息1", group_id=group_id, user_id="99999", sender_name="用户1"))
        await h.inject(group_message("消息2", group_id=group_id, user_id="88888", sender_name="用户2"))
        await h.settle(0.1)
        
        assert len(plugin.data["messages"][today][group_id]) == 2


# ---- PL-03: 配置初始化 ----

async def test_config_initialization():
    """PL-03: 配置正确初始化"""
    async with PluginTestHarness(
        plugin_names=[PLUGIN_NAME], plugins_dir=PLUGINS_DIR
    ) as h:
        plugin = h.get_plugin(PLUGIN_NAME)
        
        assert "schedule_time" in plugin.config
        assert plugin.config["schedule_time"] == "08:00"
        assert "monitored_groups" in plugin.config
        assert isinstance(plugin.config["monitored_groups"], list)
        assert "llm_api_base" in plugin.config
        assert "llm_api_key" in plugin.config
        assert "llm_model" in plugin.config
        assert "send_to_group" in plugin.config
        assert "summary_output_dir" in plugin.config


# ---- PL-04: 定时任务注册 ----

async def test_scheduled_task_registered():
    """PL-04: 定时任务正确注册"""
    async with PluginTestHarness(
        plugin_names=[PLUGIN_NAME], plugins_dir=PLUGINS_DIR
    ) as h:
        plugin = h.get_plugin(PLUGIN_NAME)
        
        scheduled_tasks = plugin.list_scheduled_tasks()
        assert "daily_summary" in scheduled_tasks


# ---- PL-05: 消息格式化 ----

async def test_format_group_messages():
    """PL-05: 消息格式化功能正常"""
    async with PluginTestHarness(
        plugin_names=[PLUGIN_NAME], plugins_dir=PLUGINS_DIR
    ) as h:
        plugin = h.get_plugin(PLUGIN_NAME)
        
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
        
        formatted = plugin.format_group_messages(test_messages)
        
        assert "用户1" in formatted
        assert "第一条消息" in formatted
        assert "用户2" in formatted
        assert "第二条消息" in formatted


# ---- PL-06: 插件卸载 ----

async def test_plugin_unloads():
    """PL-06: 插件卸载后从列表中移除"""
    harness = PluginTestHarness(plugin_names=[PLUGIN_NAME], plugins_dir=PLUGINS_DIR)
    await harness.start()
    assert PLUGIN_NAME in harness.loaded_plugins

    await harness.bot.plugin_loader.unload_plugin(PLUGIN_NAME)
    assert PLUGIN_NAME not in harness.loaded_plugins

    await harness.stop()

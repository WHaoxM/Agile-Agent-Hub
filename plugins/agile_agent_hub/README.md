# Agile Agent Hub - NcatBot 插件

基于 Agile-Agent Hub 的上下文感知任务提取功能的 NcatBot 插件，实现每日定时总结群聊消息和智能分工提取。

## 功能特性

- 📥 **消息收集** - 自动监听群聊和私聊消息，按日期分组存储
- ⚙️ **配置管理** - 支持配置定时时间、监听群组/用户、LLM API 等参数
- 👤 **精准过滤** - 可指定监听特定群组 + 特定 QQ 号，或只监听私聊消息
- ⏰ **定时任务** - 使用 NcatBot 的定时任务服务，每日自动触发总结
- 📊 **群聊总结** - 调用 LLM 生成完整的群聊总结
- 🎯 **任务提取** - 基于上下文感知的任务提取，识别任务和分工
- 🖼️ **图片总结** - 生成精美的 HTML 图片发送到群里（支持多种主题）
- 💾 **结果存储** - 将总结和任务保存到本地 JSON 文件
- 📢 **指定发送** - 可将总结发送到指定群（汇总多个群的消息到一个群）

## 安装与配置

### 1. 安装插件

将 `agile_agent_hub` 目录复制到 NcatBot 的 `plugins/` 目录下。

### 2. 安装图片生成依赖（可选但推荐）

如果启用图片总结功能，需要安装 Playwright：

```bash
# 安装 playwright
pip install playwright

# 安装 Chromium 浏览器（首次运行需要）
playwright install chromium
```

### 3. 配置插件

编辑 `config.yaml` 文件，配置以下参数：

```yaml
# 每日总结时间（HH:MM 格式）
schedule_time: "08:00"

# 监听的群组列表（空数组表示监听所有群组）
# 示例: ["1005031932", "123456789"]
monitored_groups: []

# 只监听指定用户的 QQ 号（空数组表示监听所有人）
# 示例: ["2319766011", "123456789"]
monitored_users: []
# LLM API 配置
llm_api_base: "https://api.openai.com/v1"
llm_api_key: "your-api-key-here"  # 必须填写你的 API Key
llm_model: "gpt-4o"

# 是否将总结发送到群聊
send_to_group: false

# 总结输出目录
summary_output_dir: "summaries"
```

<<<<<<< HEAD
### 配置说明

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `schedule_time` | 每日总结时间 | `"07:00"` |
| `monitored_groups` | 只监听指定群（空=所有群） | `["1005031932"]` |
| `monitored_users` | 群聊只监听指定用户（空=所有人） | `["2319766011"]` |
| `monitored_private_users` | 监听指定私聊用户（空=不监听私聊） | `["2319766011"]` |
| `send_to_group` | 是否将总结发回群内 | `false` |
| `summary_target_groups` | 总结发送到指定群（空=发送到原群） | `["1005031932"]` |
| `dynamic_summary_enabled` | 启用动态空闲总结 | `true` |
| `dynamic_summary_idle_minutes` | 空闲多少分钟后触发总结 | `10` |
| `dynamic_summary_min_messages` | 触发总结的最小消息数 | `5` |
| `summary_as_image` | 以图片形式发送总结 | `true` |
| `summary_image_theme` | 图片主题 (default/dark/colorful) | `"colorful"` |
### 3. 启动 NcatBot

```bash
ncatbot run
```

## 使用方法

### 自动模式

1. 机器人会自动收集群聊消息
2. 每日在配置的时间自动生成总结
3. 总结和任务会保存到 `summaries/` 目录

### 配置场景示例

#### 场景1: 只监听特定群
```yaml
monitored_groups: ["1005031932"]
monitored_users: []
```
只监听群号为 `1005031932` 的群，群里所有用户的消息都会被收集。

#### 场景2: 只监听特定人
```yaml
monitored_groups: []
monitored_users: ["2319766011"]
```
监听所有群，但只收集 QQ 号为 `2319766011` 的用户发送的消息。

#### 场景3: 特定群 + 特定人
```yaml
monitored_groups: ["1005031932"]
monitored_users: ["2319766011", "2536823421"]
```
只监听 `1005031932` 群，且只收集这两个 QQ 号用户的消息。

#### 场景4: 监听所有（默认）
```yaml
monitored_groups: []
monitored_users: []
```
监听所有群的所有用户消息。

#### 场景5: 只监听私聊消息
```yaml
monitored_groups: []
monitored_users: []
monitored_private_users: ["2319766011"]
```
不监听任何群聊，只收集这个 QQ 号私聊发给机器人的消息。

#### 场景6: 群聊+私聊同时监听
```yaml
monitored_groups: ["1005031932"]
monitored_users: []
monitored_private_users: ["2319766011"]
```
同时监听 `1005031932` 群的全部消息，以及 `2319766011` 私聊消息。

#### 场景7: 多群汇总到一个群发送总结
```yaml
monitored_groups: ["1005031932", "2005031932", "3005031932"]
send_to_group: true
summary_target_groups: ["1005031932"]
```
监听3个群的消息，每天将3个群的总结都发送到 `1005031932` 群。

#### 场景8: 动态空闲总结（推荐）
```yaml
monitored_groups: ["1005031932"]
send_to_group: true
summary_target_groups: ["1005031932"]
dynamic_summary_enabled: true
dynamic_summary_idle_minutes: 10
dynamic_summary_min_messages: 5
```
群聊会话结束后（10分钟内无新消息）且积累了5条以上消息时，自动触发总结并发送到群内。

#### 场景9: 动态总结 + 定时总结双模式
```yaml
# 动态总结：实时跟进会话
monitored_groups: ["1005031932"]
send_to_group: true
dynamic_summary_enabled: true
dynamic_summary_idle_minutes: 10

# 定时总结：每日回顾
schedule_time: "07:00"
```
- **会话中**：10分钟无消息时自动总结发送
- **每天早上7点**：生成完整的昨日全量总结

#### 场景10: 手动触发即时总结
在群里发送 `!总结` 命令，立即生成并发送当前会话的总结：
```
[群成员] !总结
[机器人] 🤖 [昵称] 触发了即时总结，正在生成中...
[机器人] [发送精美图片总结]
```
**注意**: 手动总结会清空今日消息缓存，避免与动态/定时总结重复。

#### 场景11: 图片总结主题选择
```yaml
# 彩色渐变主题（推荐，美观）
summary_as_image: true
summary_image_theme: "colorful"

# 深色主题
summary_image_theme: "dark"

# 简洁默认主题
summary_image_theme: "default"

# 关闭图片，使用文本
summary_as_image: false
```
生成的图片效果：
- 顶部彩色渐变头部，显示标题和时间
- 中间是会话总结正文
- 底部是任务清单（带序号、负责人、截止日期）
- 整体圆角卡片设计，美观易读

**获取群号和QQ号方法**: 启动插件后，在群里发消息，看终端日志输出：`收到群消息 - 群组: {群号}, 发送者: {昵称} ({QQ号})`
### 总结文件格式

生成的总结文件为 JSON 格式，包含以下字段：

```json
{
  "date": "2026-04-12",
  "group_id": "123456789",
  "generated_at": "2026-04-13T08:00:00.123456",
  "summary": "群聊总结内容...",
  "raw_response": "LLM 原始响应...",
  "tasks": [
    {
      "task": "任务描述",
      "assignee": "负责人",
      "deadline": "2026-04-14 15:00",
      "raw_text": "原始文本片段"
    }
  ]
}
```

## 测试

运行插件单元测试：

```bash
cd plugins/agile_agent_hub
pytest tests/
```

## 项目结构

```
agile_agent_hub/
├── __init__.py          # 插件入口
├── manifest.toml        # 插件元数据
├── config.yaml          # 默认配置文件
├── plugin.py            # 主插件类
├── models.py            # 数据模型
├── prompt.py            # 提示词模板
├── llm_client.py        # LLM 客户端
├── parser.py            # 响应解析器
├── README.md            # 本文件
└── tests/               # 测试文件
    ├── __init__.py
    └── test_plugin.py
```

## 技术栈

- **NcatBot** - QQ 机器人框架
- **OpenAI API** - LLM 调用
- **Python 3.11+** - 编程语言

## 作者

NcatBot Team

## 许可证

NcatBot License

# QQ 测试指南

本指南将帮助您在 QQ 上测试 Agile Agent Hub 插件。

## 📋 前置要求

1. **一个 QQ 账号** - 用于机器人
2. **NapCat** - OneBot11 协议实现
3. **Python 3.12+** - 运行 NcatBot
4. **LLM API Key** - 用于生成群聊总结（如 OpenAI、DeepSeek 等）

## 🚀 步骤 1: 安装 NapCat

NapCat 是 OneBot11 协议的实现，用于连接 QQ。

### 方式一：使用 NapCat 安装器（推荐）

1. 访问 [NapCat 官网](https://napneko.github.io/)
2. 下载并安装 NapCat
3. 启动 NapCat 并登录您的机器人 QQ 号
4. 在 NapCat 设置中启用 WebSocket 服务：
   - 监听地址：`127.0.0.1`
   - 端口：`3001`
   - 无需 token（或设置您自己的 token）

### 方式二：使用 Docker

```bash
docker run -d \
  --name napcat \
  -p 3001:3001 \
  -v napcat-data:/app/napcat/data \
  mlikiowa/napcat-docker:latest
```

## 🚀 步骤 2: 配置 NcatBot

### 2.1 编辑主配置文件

编辑 `/workspace/NcatBot/config.yaml`，填入您的配置：

```yaml
bot:
  # 机器人 QQ 号（必填）
  qq: 您的机器人QQ号
  # 管理员 QQ 号列表（必填）
  admins:
    - 您的管理员QQ号

adapters:
  - type: napcat
    enabled: true
    # NapCat WebSocket 地址
    ws_url: ws://127.0.0.1:3001
    # 如果您在 NapCat 中设置了 token，填入这里
    token: ""
```

### 2.2 配置 Agile Agent Hub 插件

编辑 `/workspace/plugins/agile_agent_hub/config.yaml`：

```yaml
# 每日总结时间（HH:MM 格式）
schedule_time: "08:00"

# 监听的群组列表（空数组表示监听所有群组）
# 示例：monitored_groups: ["123456789", "987654321"]
monitored_groups: []

# LLM API 配置
llm_api_base: "https://api.openai.com/v1"
# 或使用 DeepSeek："https://api.deepseek.com/v1"

llm_api_key: "您的API密钥"  # 必须填写！
llm_model: "gpt-4o"
# 或使用 DeepSeek："deepseek-chat"

# 是否将总结发送到群聊
send_to_group: false

# 总结输出目录
summary_output_dir: "summaries"
```

## 🚀 步骤 3: 启动服务

### 3.1 启动 NapCat

确保 NapCat 正在运行并且 WebSocket 服务已启用。

### 3.2 启动 NcatBot

在 `/workspace/NcatBot` 目录下运行：

```bash
cd /workspace/NcatBot
python -m ncatbot.cli.main run
```

或者如果已安装 ncatbot：

```bash
ncatbot run
```

## 🧪 步骤 4: 测试插件

### 4.1 验证插件加载

启动 NcatBot 后，您应该看到类似以下的日志：

```
INFO: AgileAgentHub 已加载
INFO: 配置信息:
INFO:   schedule_time: 08:00
INFO:   monitored_groups: []
INFO:   llm_api_base: https://api.openai.com/v1
INFO:   llm_model: gpt-4o
INFO:   send_to_group: false
INFO:   summary_output_dir: summaries
INFO: 定时任务已注册: daily_summary 于 08:00
```

### 4.2 测试消息收集

在您的 QQ 群中发送几条消息，插件会自动收集这些消息。

### 4.3 手动触发总结（可选）

如果您想立即测试总结功能而不等待定时任务，可以：

1. 修改 `plugins/agile_agent_hub/plugin.py` 中的 `schedule_time` 为当前时间稍后一点
2. 或者手动调用 `daily_summary()` 方法进行测试

## 📊 查看结果

### 总结文件

生成的总结文件会保存在 `summaries/` 目录下，文件名格式为：
`YYYY-MM-DD_群组ID_HHMMSS.json`

### 文件内容示例

```json
{
  "date": "2026-04-13",
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

## 🔧 故障排除

### 问题 1: NapCat 连接失败

**症状**: 日志显示无法连接到 NapCat

**解决方案**:
1. 确认 NapCat 正在运行
2. 检查 WebSocket 端口是否正确（默认 3001）
3. 检查防火墙设置
4. 运行诊断：`ncatbot napcat diagnose`

### 问题 2: 插件未加载

**症状**: 日志中没有显示 AgileAgentHub 加载信息

**解决方案**:
1. 确认插件目录在正确位置：`NcatBot/plugins/agile_agent_hub/`
2. 检查 `manifest.toml` 是否存在
3. 查看日志中的错误信息

### 问题 3: LLM 调用失败

**症状**: 总结生成失败，日志显示 API 错误

**解决方案**:
1. 确认 API Key 正确且有效
2. 确认 API Base URL 正确
3. 检查网络连接
4. 确认账户有足够的配额

### 问题 4: 定时任务不触发

**症状**: 到了设定时间但没有生成总结

**解决方案**:
1. 确认时间格式为 HH:MM（24小时制）
2. 检查时区设置
3. 查看日志中的定时任务注册信息

## 📚 更多资源

- **NcatBot 文档**: https://docs.ncatbot.xyz
- **NapCat 文档**: https://napneko.github.io/
- **OneBot11 协议**: https://onebot.dev/

## 💡 提示

1. **先测试小范围**: 先用一个小群测试，确认功能正常后再推广
2. **监控日志**: 保持关注 NcatBot 的日志输出，及时发现问题
3. **备份配置**: 定期备份您的配置文件
4. **更新插件**: 关注插件更新，获取新功能和修复

祝您测试顺利！🎉


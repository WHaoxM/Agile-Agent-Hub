# 🚀 快速参考卡片

## 一、环境安装

### macOS / Linux
```bash
# 1. 进入项目目录
cd /path/to/Agile-Agent-Hub

# 2. 运行自动安装脚本
./install.sh
```

### Windows
```batch
# 1. 进入项目目录
cd C:\path\to\Agile-Agent-Hub

# 2. 运行自动安装脚本
install.bat
```

### 手动安装（如果自动脚本失败）
```bash
# 1. 创建虚拟环境
python3 -m venv venv          # macOS/Linux
python -m venv venv            # Windows

# 2. 激活虚拟环境
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate.bat      # Windows

# 3. 安装依赖
pip install --upgrade pip
pip install -e .
cd NcatBot
pip install -e .[test]
cd ..

# 4. 链接插件（macOS/Linux）
cd NcatBot
mkdir -p plugins
ln -sf ../../plugins/agile_agent_hub ./plugins/agile_agent_hub

# 4. 复制插件（Windows）
cd NcatBot
mkdir plugins
xcopy /E /I "..\plugins\agile_agent_hub" "plugins\agile_agent_hub"
```

---

## 二、配置文件

### 1. NcatBot/config.yaml
```yaml
bot:
  qq: 您的机器人QQ号
  admins:
    - 您的管理员QQ号

adapters:
  - type: napcat
    enabled: true
    ws_url: ws://127.0.0.1:3001
    token: ""
```

### 2. plugins/agile_agent_hub/config.yaml
```yaml
schedule_time: "08:00"
monitored_groups: []
llm_api_base: "https://api.openai.com/v1"
llm_api_key: "sk-您的API密钥"    # ⚠️ 必须替换！
llm_model: "gpt-4o"
send_to_group: false
summary_output_dir: "summaries"
```

---

## 三、启动服务

### 1. 启动 NapCat
- 下载：https://napneko.github.io/
- 登录机器人 QQ
- 启用 WebSocket（端口 3001）

### 2. 启动 NcatBot
```bash
cd /path/to/Agile-Agent-Hub/NcatBot

# 激活虚拟环境
source ../venv/bin/activate       # macOS/Linux
..\venv\Scripts\activate.bat      # Windows

# 启动
python -m ncatbot.cli.main run
```

---

## 四、测试验证

### 运行测试
```bash
cd /path/to/Agile-Agent-Hub/plugins/agile_agent_hub

# 防御性工具测试
python tests/test_defensive_utils.py

# 集成测试
python tests/test_integration.py
```

### 检查日志
启动 NcatBot 后，确认看到：
```
INFO: AgileAgentHub 已加载
INFO: 定时任务已注册: daily_summary 于 08:00
```

---

## 五、常用命令速查

```bash
# 项目根目录
cd /path/to/Agile-Agent-Hub

# 激活虚拟环境
source venv/bin/activate          # macOS/Linux
venv\Scripts\activate             # Windows

# 启动 NcatBot
cd NcatBot
python -m ncatbot.cli.main run

# 查看生成的总结
ls -la NcatBot/summaries/         # macOS/Linux
dir NcatBot\summaries              # Windows
```

---

## 六、文档索引

| 文档 | 说明 |
|------|------|
| [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) | 完整安装指南 |
| [QQ_TEST_GUIDE.md](QQ_TEST_GUIDE.md) | QQ 测试指南 |
| [plugins/agile_agent_hub/README.md](plugins/agile_agent_hub/README.md) | 插件使用说明 |
| [PROJECT_STATE.md](PROJECT_STATE.md) | 项目状态 |

---

## 七、故障排除快速链接

- Python 版本问题 → 确认 Python 3.12+
- 虚拟环境问题 → 重新激活虚拟环境
- NapCat 连接 → 确认 NapCat 运行且 WebSocket 启用
- 插件未加载 → 检查 NcatBot/plugins/agile_agent_hub/ 存在
- LLM 调用失败 → 确认 API Key 正确

---

## 💡 提示

1. **先看文档**：首次安装请先阅读 [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
2. **分步验证**：每完成一步都验证一下，不要跳过
3. **查看日志**：遇到问题先看日志输出
4. **备份配置**：配置好后备份配置文件


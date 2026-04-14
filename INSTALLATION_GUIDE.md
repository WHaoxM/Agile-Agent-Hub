# 完整环境安装指南

本指南将帮助您在全新环境中完整安装 Agile-Agent Hub + NcatBot 项目。

---

## 📋 环境要求

- **操作系统**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)
- **Python**: 3.12 或更高版本
- **内存**: 至少 4GB RAM
- **磁盘空间**: 至少 2GB 可用空间

---

## 🚀 第一步：安装 Python

### Windows
1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.12 或更高版本
3. 运行安装程序，**务必勾选 "Add Python to PATH"**
4. 验证安装：打开命令提示符，输入 `python --version`

### macOS
```bash
# 使用 Homebrew 安装（推荐）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.12

# 验证安装
python3 --version
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip -y

# 验证安装
python3.12 --version
```

---

## 🚀 第二步：下载项目

### 方式一：使用 Git（推荐）
```bash
# 克隆项目
git clone <您的项目仓库地址>
cd Agile-Agent-Hub

# 如果您是从当前工作目录直接复制，请确保整个项目目录完整复制
```

### 方式二：直接下载
1. 下载项目 ZIP 文件
2. 解压到您想要的目录
3. 进入项目目录

---

## 🚀 第三步：设置 Python 虚拟环境（推荐）

### Windows
```bash
# 在项目目录下
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 验证虚拟环境已激活（命令提示符前会有 (venv)）
```

### macOS / Linux
```bash
# 在项目目录下
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 验证虚拟环境已激活（命令提示符前会有 (venv)）
```

---

## 🚀 第四步：安装项目依赖

### 在虚拟环境中（如果使用了虚拟环境）
```bash
# 确保在项目根目录
cd /path/to/Agile-Agent-Hub

# 升级 pip
pip install --upgrade pip

# 安装主项目依赖
pip install -e .

# 进入 NcatBot 目录并安装依赖
cd NcatBot
pip install -e .[test]

# 返回项目根目录
cd ..
```

### 验证依赖安装
```bash
# 检查 Python 版本
python --version

# 检查已安装的包
pip list
```

---

## 🚀 第五步：安装 NapCat（QQ 连接）

### 什么是 NapCat？
NapCat 是一个 OneBot11 协议的实现，用于连接 QQ。

### Windows（推荐）
1. 访问 https://napneko.github.io/
2. 下载 NapCat.Windows.zip
3. 解压到任意目录
4. 运行 `NapCat.exe`
5. 扫码登录您的机器人 QQ 号
6. **重要**：在设置中启用 WebSocket 服务
   - 监听地址：`127.0.0.1`
   - 端口：`3001`
   - 不需要 Token（留空）

### macOS / Linux（使用 Docker）
```bash
# 拉取镜像
docker pull mlikiowa/napcat-docker:latest

# 运行容器
docker run -d \
  --name napcat \
  -p 3001:3001 \
  -v napcat-data:/app/napcat/data \
  mlikiowa/napcat-docker:latest

# 查看日志并按提示登录
docker logs -f napcat
```

---

## 🚀 第六步：配置项目

### 6.1 配置 NcatBot 主配置

编辑 `NcatBot/config.yaml`：

```bash
# 复制模板（如果还没有）
cd /path/to/Agile-Agent-Hub/NcatBot
# 如果没有 config.yaml，我已经为您创建了一个模板
```

编辑 `config.yaml`，填入：
```yaml
bot:
  # 您的机器人 QQ 号
  qq: 123456789
  # 管理员 QQ 号（您自己的 QQ）
  admins:
    - 987654321

adapters:
  - type: napcat
    enabled: true
    ws_url: ws://127.0.0.1:3001
    token: ""
```

### 6.2 配置 Agile Agent Hub 插件

编辑 `plugins/agile_agent_hub/config.yaml`：

```yaml
# 每日总结时间
schedule_time: "08:00"

# 监听的群组（空数组=监听所有）
monitored_groups: []

# LLM API 配置（必填！）
llm_api_base: "https://api.openai.com/v1"
# 或使用 DeepSeek："https://api.deepseek.com/v1"

llm_api_key: "sk-您的真实API密钥"  # 必须替换为您的真实 Key！

llm_model: "gpt-4o"
# 或使用 DeepSeek："deepseek-chat"

# 是否发送到群聊
send_to_group: false

# 输出目录
summary_output_dir: "summaries"
```

### 6.3 链接插件到 NcatBot

```bash
cd /path/to/Agile-Agent-Hub/NcatBot

# 创建 plugins 目录（如果不存在）
mkdir -p plugins

# 链接插件
ln -sf ../../plugins/agile_agent_hub ./plugins/agile_agent_hub

# 或者 Windows 上使用复制
# xcopy /E /I "..\..\plugins\agile_agent_hub" "plugins\agile_agent_hub"
```

---

## 🚀 第七步：验证安装

### 7.1 运行测试

```bash
# 1. 测试防御性工具模块
cd /path/to/Agile-Agent-Hub/plugins/agile_agent_hub
python tests/test_defensive_utils.py

# 2. 测试集成
python tests/test_integration.py
```

### 7.2 检查所有文件位置

确保以下文件存在：
```
Agile-Agent-Hub/
├── plugins/
│   └── agile_agent_hub/
│       ├── __init__.py
│       ├── manifest.toml
│       ├── config.yaml
│       ├── plugin.py
│       ├── models.py
│       ├── prompt.py
│       ├── llm_client.py
│       ├── parser.py
│       ├── defensive_utils.py
│       └── tests/
└── NcatBot/
    ├── config.yaml
    ├── plugins/
    │   └── agile_agent_hub -> ../../plugins/agile_agent_hub
    └── ...
```

---

## 🚀 第八步：启动并测试

### 8.1 启动 NapCat

确保 NapCat 正在运行并且已登录 QQ。

### 8.2 启动 NcatBot

```bash
cd /path/to/Agile-Agent-Hub/NcatBot

# 启动 NcatBot
python -m ncatbot.cli.main run
```

### 8.3 观察日志

您应该看到类似以下日志：
```
INFO: AgileAgentHub 已加载
INFO: 配置信息:
INFO:   schedule_time: 08:00
INFO: 定时任务已注册: daily_summary 于 08:00
```

### 8.4 在 QQ 中测试

1. 确保您的机器人和您在同一个群
2. 在群里发送几条消息
3. 观察 NcatBot 日志，确认消息被收集
4.（可选）修改 `schedule_time` 为当前时间稍后几分钟，测试定时总结

---

## 🔧 常见问题解决

### 问题 1: Python 版本不兼容
**症状**: `ModuleNotFoundError` 或语法错误
**解决**: 确认使用 Python 3.12+
```bash
python --version
which python
```

### 问题 2: 虚拟环境未激活
**症状**: 安装的包找不到
**解决**: 重新激活虚拟环境
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 问题 3: NapCat 连接失败
**症状**: WebSocket 连接错误
**解决**:
1. 确认 NapCat 正在运行
2. 确认 WebSocket 端口是 3001
3. 检查防火墙设置

### 问题 4: 插件未加载
**症状**: 日志中没有 AgileAgentHub
**解决**:
1. 确认插件在 `NcatBot/plugins/agile_agent_hub/`
2. 检查 `manifest.toml` 是否存在
3. 查看完整日志找错误

---

## 📚 下一步

完成安装后，请参考：
- **[QQ 测试指南](QQ_TEST_GUIDE.md)** - 详细的 QQ 测试步骤
- **[插件 README](plugins/agile_agent_hub/README.md)** - 插件使用说明
- **[NcatBot 文档](https://docs.ncatbot.xyz)** - NcatBot 官方文档

---

## 💡 快速命令速查

```bash
# 进入项目目录
cd /path/to/Agile-Agent-Hub

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 启动 NcatBot
cd NcatBot
python -m ncatbot.cli.main run

# 运行测试
cd ../plugins/agile_agent_hub
python tests/test_defensive_utils.py
python tests/test_integration.py
```

---

祝您安装顺利！🎉

如有问题，请检查日志或参考故障排除部分。


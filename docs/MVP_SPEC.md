# Agile-Agent Hub - MVP 需求规格与边界协议

## 1. 核心用例 (Use Cases)

### 用例 1：从聊天文本提取任务
- **输入**：一段 QQ 群聊文本（手动粘贴）
- **处理**：LLM 分析并提取任务信息
- **输出**：
  - JSON 格式：`[{"task": "任务描述", "assignee": "负责人", "deadline": "截止时间", "raw_text": "原始消息"}]`
  - Markdown 格式：清晰的任务清单表格

### 用例 2：任务去重与合并
- **输入**：包含重复任务的聊天记录
- **处理**：识别相似任务并合并
- **输出**：去重后的任务清单

## 2. 必须接入的外部 API (External APIs)
- **无** - MVP 阶段使用本地 LLM 或通过 SOLO 平台的 LLM 能力

## 3. 数据流向图描述 (Data Flow)
```
用户粘贴 QQ 群聊文本 
    ↓
文本输入模块
    ↓
LLM 任务提取 Agent
    ↓
任务结构化模块
    ↓
JSON 输出 + Markdown 输出
```

## 4. 绝对不做的功能清单 (Not-to-do List)
- ❌ QQ 机器人自动监听（[Phase 2]）
- ❌ 多租户/权限系统（[Phase 2]）
- ❌ 网页可视化看板（[Phase 2]）
- ❌ 微信/飞书等多平台支持（[Phase 2]）
- ❌ 任务状态追踪（[Phase 2]）
- ❌ 通知推送功能（[Phase 2]）

## 5. 技术栈确认
- Python 3.10+
- pytest + pytest-cov
- LLM 能力（通过 SOLO 平台）

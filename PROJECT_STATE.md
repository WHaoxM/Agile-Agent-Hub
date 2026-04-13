# [项目 SSOT] Agile-Agent Hub

## 1. 当前架构 (Current_Architecture)
- **项目目标:** 将 QQ 群聊非结构化聊天记录提取为标准化待办任务的本地智能体流水线。
- **技术栈:** Python 3.10+, pytest, pytest-cov, LLM (通过 SOLO 平台)。
- **目录结构:**
  - `src/` - 源代码目录
  - `tests/` - 测试代码目录
  - `docs/` - 文档目录
- **依赖管理:** pyproject.toml
- **输出格式:** JSON + Markdown 双输出
- **核心数据模型:** [src/models.py](file:///workspace/src/models.py) - Task dataclass
- **输出模块:** [src/output.py](file:///workspace/src/output.py) - tasks_to_json, tasks_to_markdown
- **提取模块:** [src/extractor.py](file:///workspace/src/extractor.py) - TaskExtractor (支持 LLM 提取 + mock 提取)
  - LLM 提取：使用 OpenAI 兼容 API 进行智能任务提取
  - Mock 提取：简单模式匹配作为降级方案
- **LLM 客户端:** [src/llm_client.py](file:///workspace/src/llm_client.py) - LLM API 调用封装
- **配置模块:** [src/config.py](file:///workspace/src/config.py) - LLM 配置管理
- **完整流水线:** [src/pipeline.py](file:///workspace/src/pipeline.py) - TaskPipeline

## 2. 当前开发阶段 (Active_Task)
- **Phase:** 04_LLM_Integration (LLM 集成完成！)
- **MVP 规格文档:** [docs/MVP_SPEC.md](file:///workspace/docs/MVP_SPEC.md)
- **当前冲刺任务:**
  - [x] 定义任务数据模型（Task dataclass）
  - [x] 实现 JSON + Markdown 双输出模块
  - [x] 实现 LLM 任务提取功能（mock 版本）
  - [x] 实现完整流水线 (TaskPipeline)
  - [x] 实现真实 LLM API 集成（OpenAI 兼容接口）
  - [x] 添加环境变量配置支持
  - [x] 实现 LLM 提取失败降级机制

## 3. 已完成特性 (Completed_Features)
- **基础设施搭建:** 完成项目目录结构，配置 pytest 测试框架
- **测试套件初始化:** 2个测试用例（test_dummy 和 test_text_input）全部通过
- **项目配置:** 创建 pyproject.toml 配置文件
- **MVP 规格定义:** 完成 docs/MVP_SPEC.md，明确核心用例与边界
- **数据模型定义:** 完成 Task dataclass，4个测试用例全部通过
- **双输出模块:** 完成 tasks_to_json 和 tasks_to_markdown，5个测试用例全部通过
- **LLM 提取模块:** 完成 TaskExtractor 接口与 mock 实现，10个测试用例通过
- **完整流水线:** 完成 TaskPipeline，7个测试用例通过，总计28个测试用例全部通过！
- **LLM 集成:** 
  - 实现 OpenAI 兼容 API 客户端（src/llm_client.py）
  - 实现环境变量配置管理（src/config.py）
  - 支持自定义 API 地址、模型和超时时间
  - 实现 LLM 提取失败自动降级到 mock 提取
  - 添加 .env.example 配置示例文件
  - 更新 example.py 包含详细的使用说明

## 4. 废弃区与上下文垃圾桶 (Deprecated_Info)
- None

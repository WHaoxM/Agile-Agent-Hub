# Agile-Agent Hub - 上下文感知任务提取器 - Product Requirement Document

## Overview
- **Summary**: 构建一个能够理解长群聊上下文、智能补全省略信息、一次性提取所有结构化任务的 MVP 工具。
- **Purpose**: 解决长群聊中任务信息分散、需要人工翻找和补全上下文的痛点。
- **Target Users**: 团队开发人员、项目管理者、任何需要从群聊中提取任务的人。

## Goals
- 支持输入任意长度的群聊文本，自动理解多轮对话上下文
- 能够智能补全省略的主语、宾语和时间信息
- 一次性提取所有结构化任务，包含任务描述、负责人、截止时间
- 保持与现有 TaskExtractor 接口的向后兼容性

## Non-Goals (Out of Scope)
- 不实现实时消息监听功能
- 不实现任务状态追踪和同步
- 不实现多人协作编辑功能
- 不实现任务提醒或通知功能
- 不实现任务优先级排序
- 不实现任务标签或分类

## Background & Context
- 现有系统已有基础的 TaskExtractor，但只能处理单条消息，无法理解上下文
- 现有系统已集成 DeepSeek LLM，可用于增强理解能力
- 用户提供的示例显示真实群聊中任务信息非常分散，需要智能理解
- 技术栈为 Python 3.10+，已有完整的测试框架

## Functional Requirements
- **FR-1**: 支持输入任意长度的群聊文本（多行、多轮对话）
- **FR-2**: 能够理解对话上下文，识别发言人和指代关系
- **FR-3**: 能够智能补全省略的主语、宾语和时间信息
- **FR-4**: 能够区分闲聊和真正的任务指令
- **FR-5**: 一次性提取所有结构化任务（Task 对象列表）
- **FR-6**: 保持与现有 extract_tasks() 接口的兼容性

## Non-Functional Requirements
- **NFR-1**: LLM 调用超时时间应可配置（默认 60 秒）
- **NFR-2**: 错误消息应清晰，包含错误类型和上下文
- **NFR-3**: 代码应保持向后兼容，不破坏现有调用方
- **NFR-4**: 测试覆盖率应保持在 80% 以上
- **NFR-5**: 长文本处理应在合理时间内完成（< 2 分钟）

## Constraints
- **Technical**: 
  - 必须使用 Python 3.10+
  - 保持与现有 Task 数据模型兼容
  - 遵循现有代码风格和防御性编程原则
  - 必须使用现有 LLM 集成基础设施
- **Business**: 
  - 开发时间应控制在 1-2 个会话内
- **Dependencies**: 
  - 依赖现有 LLM 客户端和配置模块

## Assumptions
- 用户已有可用的 LLM API 密钥
- LLM 能够理解中文长文本对话
- 网络连接可用，能够访问 LLM API
- 群聊输入格式为纯文本，每行一条消息

## Acceptance Criteria

### AC-1: 长文本输入支持
- **Given**: 系统已配置有效的 LLM API 密钥
- **When**: 传入包含多轮对话的长群聊文本
- **Then**: 系统能够处理并理解整个上下文
- **Verification**: `programmatic`

### AC-2: 上下文理解和指代识别
- **Given**: 群聊中包含省略主语/宾语的对话（如"你去做这个"）
- **When**: 提取任务时
- **Then**: 系统能够正确识别指代关系，补全省略的信息
- **Verification**: `programmatic`（通过特定测试用例）

### AC-3: 智能任务补全
- **Given**: 群聊中缺少明确的截止时间或负责人
- **When**: 提取任务时
- **Then**: 系统能够根据上下文合理推断或标记为缺失
- **Verification**: `programmatic`

### AC-4: 闲聊过滤
- **Given**: 群聊中包含闲聊和任务指令的混合
- **When**: 提取任务时
- **Then**: 系统只提取真正的任务指令，忽略闲聊
- **Verification**: `programmatic`

### AC-5: 多任务提取
- **Given**: 群聊中包含多个任务
- **When**: 提取任务时
- **Then**: 系统能够一次性提取所有任务
- **Verification**: `programmatic`

### AC-6: 接口兼容性
- **Given**: 现有代码调用 TaskExtractor.extract_tasks()
- **When**: 使用新的上下文感知实现
- **Then**: 现有代码无需修改即可正常工作
- **Verification**: `programmatic`（通过现有测试）

## Open Questions
- [ ] 群聊消息的格式是什么？（每行一条消息？带时间戳？）
- [ ] 是否需要支持@提及的特殊格式？
- [ ] 最长支持多长的输入文本？

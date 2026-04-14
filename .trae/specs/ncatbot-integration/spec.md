# NcatBot + Agile-Agent Hub 集成 - Product Requirement Document

## Overview
- **Summary**: 将 Agile-Agent Hub 的上下文感知任务提取功能集成到 NcatBot 框架中，实现每日定时总结群聊消息和智能分工提取。
- **Purpose**: 解决群聊中任务分散、信息遗漏、分工不明确的问题，通过 AI 自动整理和分发任务，提高团队协作效率。
- **Target Users**: 使用 QQ 群进行协作的团队、项目组、学习小组。

## Goals
1. 实现群聊消息的自动收集和持久化存储
2. 集成上下文感知任务提取功能，从长群聊中识别任务和分工
3. 提供可配置的定时任务，每日自动生成总结和任务清单
4. 将结果存储到本地文件，并支持发送到群聊

## Non-Goals (Out of Scope)
- 不实现实时的单条消息处理（仅批量总结）
- 不实现任务状态的追踪和更新
- 不实现多轮对话交互（仅生成总结）
- 不涉及数据库集成（仅本地文件存储）

## Background & Context
- Agile-Agent Hub 已成功实现上下文感知任务提取功能（`feature/context-aware-extractor` 分支）
- NcatBot 是基于 OneBot11 协议的成熟 Python QQ 机器人框架，提供插件系统、定时任务、数据持久化等功能
- 用户需要完整的自动化方案，包括消息收集、LLM 调用、总结生成、任务提取、本地存储

## Functional Requirements
- **FR-1**: 消息收集功能 - 监听群聊消息并按日期和群组持久化存储
- **FR-2**: 配置管理 - 支持配置定时时间、监听群组、LLM API 等参数
- **FR-3**: 定时任务调度 - 每日在指定时间触发总结生成
- **FR-4**: 上下文感知提取 - 调用 Agile-Agent Hub 的功能生成总结和任务清单
- **FR-5**: 结果存储 - 将生成的总结和任务保存到本地 JSON 文件
- **FR-6**: 群聊通知（可选）- 将总结发送到对应群聊

## Non-Functional Requirements
- **NFR-1**: 可配置性 - 所有关键参数应通过配置文件管理，无需修改代码
- **NFR-2**: 容错性 - LLM 调用失败时有降级处理（使用简单提示词）
- **NFR-3**: 数据持久化 - 所有消息和生成的结果应保存到本地，重启不丢失
- **NFR-4**: 性能 - 定时任务应在合理时间内完成（≤ 5 分钟）

## Constraints
- **Technical**: 必须基于 NcatBot 框架开发插件，使用 Python 3.11+
- **Business**: 必须使用用户已有的 Agile-Agent Hub 代码库，避免重复开发
- **Dependencies**: 
  - NcatBot 框架
  - Agile-Agent Hub 的上下文感知提取模块
  - LLM API（OpenAI 兼容）

## Assumptions
- 用户已有可用的 LLM API 密钥
- NcatBot 已配置好与 QQ 的连接（NapCat）
- 目标群组已添加机器人为好友或群成员

## Acceptance Criteria

### AC-1: 消息收集功能
- **Given**: 机器人已加入目标群组并运行
- **When**: 群成员发送消息
- **Then**: 消息被自动记录并存储到 `data.json`，按日期和群组分组
- **Verification**: `programmatic`

### AC-2: 配置管理
- **Given**: 插件已安装
- **When**: 用户修改 `config.yaml` 中的参数
- **Then**: 插件加载时使用新配置，包括定时时间、群组列表、LLM 配置
- **Verification**: `programmatic`

### AC-3: 定时任务调度
- **Given**: 插件已配置定时时间
- **When**: 到达指定时间
- **Then**: 定时任务自动触发，开始执行总结生成流程
- **Verification**: `programmatic`

### AC-4: 上下文感知提取
- **Given**: 有收集的群聊消息
- **When**: 定时任务触发或手动触发
- **Then**: 
  1. 调用 LLM 生成完整的群聊总结
  2. 使用上下文感知提取器识别所有任务和分工
  3. 包含降级机制（上下文感知 → LLM → Mock）
- **Verification**: `programmatic`

### AC-5: 结果存储
- **Given**: 总结和任务已生成
- **When**: 生成完成后
- **Then**: 结果以 JSON 格式保存到本地文件，包含时间戳、总结内容、任务列表
- **Verification**: `programmatic`

### AC-6: 错误处理和降级
- **Given**: LLM API 调用失败或超时时
- **When**: 执行总结生成时
- **Then**: 系统自动降级到更简单的策略，记录错误但不崩溃
- **Verification**: `programmatic`

## Open Questions
- [ ] 总结是否需要默认发送到群聊？还是仅本地存储？
- [ ] 是否需要支持手动触发总结生成（通过群聊命令）？
- [ ] 总结文件的命名和存储路径是否需要可配置？

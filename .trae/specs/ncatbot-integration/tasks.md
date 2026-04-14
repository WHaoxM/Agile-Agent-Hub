# NcatBot + Agile-Agent Hub 集成 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 项目初始化与插件结构搭建
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 创建 `plugins/agile_agent_hub` 目录
  - 创建 `manifest.toml` 插件元数据文件
  - 创建基础插件类框架
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-1.1: 插件目录结构正确
  - `programmatic` TR-1.2: `manifest.toml` 包含必要字段
  - `programmatic` TR-1.3: 插件类继承 `NcatBotPlugin` 并集成所需 Mixin
- **Notes**: 使用 NcatBot CLI 模板作为参考

## [x] Task 2: 配置管理实现
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 创建默认 `config.yaml`（定时时间、群组列表、LLM 配置等）
  - 在 `on_load` 中初始化默认配置
  - 验证配置读取功能
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: 配置文件包含所有必需参数
  - `programmatic` TR-2.2: `init_defaults()` 正确设置默认值
  - `programmatic` TR-2.3: `get_config()` 能正确读取配置
- **Notes**: 配置参数包括：schedule_time, monitored_groups, llm_api_base, llm_api_key, llm_model

## [x] Task 3: 消息收集功能实现
- **Priority**: P0
- **Depends On**: Task 2
- **Description**: 
  - 使用 `EventMixin` 注册群聊消息事件处理器
  - 将消息按日期和群组 ID 分组存储到 `self.data`
  - 使用 `DataMixin` 自动持久化
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-3.1: 群聊消息被正确捕获
  - `programmatic` TR-3.2: 消息按日期和群组正确分组
  - `programmatic` TR-3.3: 数据正确保存到 `data.json`
- **Notes**: 消息结构应包含：sender_id, sender_name, content, timestamp

## [x] Task 4: Agile-Agent Hub 模块集成
- **Priority**: P0
- **Depends On**: Task 3
- **Description**: 
  - 复制/引用 Agile-Agent Hub 的核心模块（`src/prompt.py`, `src/llm_client.py`, `src/extractor.py`）
  - 调整模块以适配插件环境
  - 封装提取功能为插件内部方法
- **Acceptance Criteria Addressed**: AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-4.1: 模块正确导入且无错误
  - `programmatic` TR-4.2: 封装的提取方法可调用
  - `programmatic` TR-4.3: 降级机制正常工作
- **Notes**: 确保不破坏原有的 Agile-Agent Hub 代码

## [x] Task 5: 定时任务调度实现
- **Priority**: P0
- **Depends On**: Task 4
- **Description**: 
  - 使用 `TimeTaskMixin` 在 `on_load` 中注册定时任务
  - 实现定时任务回调方法，触发总结生成流程
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-5.1: 定时任务成功注册
  - `programmatic` TR-5.2: 任务回调方法正确实现
  - `human-judgment` TR-5.3: 任务调度配置使用配置文件中的时间
- **Notes**: 任务名称建议为 `daily_summary`

## [x] Task 6: 总结生成与结果存储
- **Priority**: P0
- **Depends On**: Task 5
- **Description**: 
  - 实现完整的总结生成流程：获取当天消息 → 调用 LLM 生成总结和任务 → 保存结果
  - 将结果保存到本地 JSON 文件（带时间戳）
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-6.1: 总结生成流程完整执行
  - `programmatic` TR-6.2: 结果文件正确创建，格式符合要求
  - `programmatic` TR-6.3: 包含错误处理和降级逻辑
- **Notes**: 结果文件建议保存在 `summaries/` 目录下

## [x] Task 7: 群聊通知（可选功能）
- **Priority**: P1
- **Depends On**: Task 6
- **Description**: 
  - 实现将总结发送到群聊的功能
  - 通过配置开关控制是否启用
- **Acceptance Criteria Addressed**: （可选）
- **Test Requirements**:
  - `programmatic` TR-7.1: 消息成功发送到群聊
  - `programmatic` TR-7.2: 配置开关正常工作
- **Notes**: 使用 NcatBot 的 Bot API 发送消息

## [x] Task 8: 测试与验证
- **Priority**: P1
- **Depends On**: Task 7
- **Description**: 
  - 编写插件单元测试
  - 端到端测试完整流程
  - 验证所有验收标准
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-8.1: 所有单元测试通过
  - `human-judgment` TR-8.2: 端到端流程验证成功
  - `programmatic` TR-8.3: 所有验收标准验证通过
- **Notes**: 使用 NcatBot 的测试框架

## [x] Task 9: 文档与示例
- **Priority**: P2
- **Depends On**: Task 8
- **Description**: 
  - 更新插件 README
  - 添加配置说明
  - 创建使用示例
- **Acceptance Criteria Addressed**: （文档）
- **Test Requirements**:
  - `human-judgment` TR-9.1: README 文档完整清晰
  - `human-judgment` TR-9.2: 配置说明详细准确
- **Notes**: 保持文档简洁实用

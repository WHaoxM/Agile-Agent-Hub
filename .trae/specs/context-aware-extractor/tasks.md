# Agile-Agent Hub - 上下文感知任务提取器 - 实施计划

## [x] Task 1: 设计并实现上下文感知提示词
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 设计新的提示词，专门用于理解长群聊上下文
  - 提示词应包含指导 LLM 理解对话历史、识别指代关系的说明
  - 提示词应包含示例，展示如何从多轮对话中提取任务
  - 保持与现有提示词模块的兼容性
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-4]
- **Test Requirements**:
  - `programmatic` TR-1.1: 提示词包含上下文理解的明确指导
  - `programmatic` TR-1.2: 提示词包含多轮对话示例
  - `human-judgement` TR-1.3: 提示词逻辑清晰，易于理解
- **Notes**: 在 src/prompt.py 中添加新的提示词构建函数

## [x] Task 2: 实现上下文感知 LLM 调用
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 在 src/llm_client.py 中添加上下文感知的 LLM 调用函数
  - 支持更长的输入文本（调整超时时间）
  - 保持与现有 LLM 客户端的兼容性
- **Acceptance Criteria Addressed**: [AC-1, AC-5, NFR-1, NFR-5]
- **Test Requirements**:
  - `programmatic` TR-2.1: 能够处理长文本输入
  - `programmatic` TR-2.2: 超时时间可配置
  - `programmatic` TR-2.3: 错误处理保持一致
- **Notes**: 复用现有的 call_llm_for_task_extraction 函数逻辑

## [x] Task 3: 重构 TaskExtractor，添加上下文感知提取方法
- **Priority**: P0
- **Depends On**: Task 2
- **Description**: 
  - 在 TaskExtractor 中添加 _context_aware_extract() 方法
  - 优先使用上下文感知提取，失败时降级到现有方法
  - 保持 extract_tasks() 接口签名不变
- **Acceptance Criteria Addressed**: [AC-5, AC-6]
- **Test Requirements**:
  - `programmatic` TR-3.1: extract_tasks() 接口保持兼容
  - `programmatic` TR-3.2: 上下文感知失败时自动降级
  - `programmatic` TR-3.3: 现有测试全部通过
- **Notes**: 保留 _llm_extract() 和 _mock_extract() 作为降级方案

## [x] Task 4: 编写上下文感知提取的测试用例
- **Priority**: P0
- **Depends On**: Task 3
- **Description**: 
  - 为长文本输入编写测试
  - 为上下文理解和指代识别编写测试
  - 为闲聊过滤编写测试
  - 为多任务提取编写测试
  - 使用 mock 测试，避免真实 LLM 调用
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-4, AC-5, AC-6]
- **Test Requirements**:
  - `programmatic` TR-4.1: 所有新功能都有对应的测试
  - `programmatic` TR-4.2: 使用 mock 测试 LLM 调用
  - `programmatic` TR-4.3: 测试覆盖率保持在 80% 以上
  - `programmatic` TR-4.4: 现有 71 个测试全部通过
- **Notes**: 在 tests/test_extractor.py 中添加新测试

## [x] Task 5: 创建示例脚本展示新功能
- **Priority**: P1
- **Depends On**: Task 4
- **Description**: 
  - 创建 test_long_chat.py 示例脚本
  - 使用用户提供的真实群聊示例
  - 展示上下文感知提取的效果
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-4, AC-5]
- **Test Requirements**:
  - `human-judgement` TR-5.1: 示例脚本能够正确运行
  - `human-judgement` TR-5.2: 输出清晰展示上下文理解效果
- **Notes**: 使用用户提供的群聊示例作为测试输入

## [x] Task 6: 更新文档
- **Priority**: P1
- **Depends On**: Task 5
- **Description**: 
  - 更新 PROJECT_STATE.md，记录新功能
  - 更新 example.py，添加上下文感知功能的说明
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `programmatic` TR-6.1: PROJECT_STATE.md 准确反映新功能
  - `human-judgement` TR-6.2: example.py 包含清晰的说明
- **Notes**: 保持文档简洁明了

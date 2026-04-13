TASK_EXTRACTION_PROMPT = """你是一个专业的任务提取助手。请从给定的聊天文本中提取所有待办任务。

## 输入格式
输入是一段中文群聊文本，可能包含一个或多个待办任务。

## 输出格式
请返回一个 JSON 数组，每个元素包含以下字段：
- task: 字符串，任务描述（必填）
- assignee: 字符串或 null，负责人姓名（可选）
- deadline: 字符串或 null，截止时间（可选，格式如 "2026-04-14 15:00"）
- raw_text: 字符串，原始的任务相关文本片段（必填）

## 示例
输入："@张三 明天下午3点前把API文档写好 @李四 后天上午10点前修复登录bug"
输出：
[
  {{
    "task": "写API文档",
    "assignee": "张三",
    "deadline": "2026-04-14 15:00",
    "raw_text": "@张三 明天下午3点前把API文档写好"
  }},
  {{
    "task": "修复登录bug",
    "assignee": "李四",
    "deadline": "2026-04-15 10:00",
    "raw_text": "@李四 后天上午10点前修复登录bug"
  }}
]

## 注意事项
1. 如果没有找到任何任务，返回空数组 []
2. 只返回 JSON，不要包含任何其他文本或解释
3. 截止时间请根据当前日期（{current_date}）推断
4. 保持任务描述简洁明了
5. raw_text 字段应该包含与该任务相关的原始文本片段

现在开始处理以下输入：
{chat_text}
"""


def build_task_extraction_prompt(chat_text: str, current_date: str) -> str:
    return TASK_EXTRACTION_PROMPT.format(
        chat_text=chat_text,
        current_date=current_date
    )


CONTEXT_AWARE_EXTRACTION_PROMPT = """你是一个专业的上下文感知任务提取助手。请从给定的长群聊历史中提取所有待办任务。

## 输入格式
输入是一段长的中文群聊历史文本，按时间顺序排列，可能包含多个主题和多个待办任务。

## 核心工作流程
1. **对话历史理解**：首先通读整个对话历史，理解对话的背景、主题发展和上下文关系
2. **指代关系识别**：准确识别指代消解（如"它"、"这个"、"那个"等代词所指代的具体内容）
3. **上下文关联**：将分散在对话不同位置的相关信息整合起来
4. **任务提取**：基于完整的上下文理解，提取所有待办任务

## 输出格式
请返回一个 JSON 数组，每个元素包含以下字段：
- task: 字符串，任务描述（必填，必须基于完整上下文理解，使用明确的表述）
- assignee: 字符串或 null，负责人姓名（可选）
- deadline: 字符串或 null，截止时间（可选，格式如 "2026-04-14 15:00"）
- raw_text: 字符串，包含所有相关的原始文本片段（必填，可能是多个句子的组合）

## 多轮对话示例
输入：
'''张三: 我们下周需要做项目演示
李四: 好的，我准备演示文稿
王五: 演示几点开始？
张三: 下午2点，在会议室A
李四: 对了，演示前需要把最新数据也加上
张三: 没错，王五你负责更新数据
王五: 好的，我在周五前完成'''

输出：
[
  {{
    "task": "准备项目演示文稿",
    "assignee": "李四",
    "deadline": null,
    "raw_text": "李四：好的，我准备演示文稿"
  }},
  {{
    "task": "在周五前更新项目最新数据",
    "assignee": "王五",
    "deadline": "2026-04-17 00:00",
    "raw_text": "李四：对了，演示前需要把最新数据也加上\n张三：没错，王五你负责更新数据\n王五：好的，我在周五前完成"
  }},
  {{
    "task": "组织下周三下午2点在会议室A的项目演示",
    "assignee": "张三",
    "deadline": "2026-04-16 14:00",
    "raw_text": "张三：我们下周需要做项目演示\n王五：演示几点开始？\n张三：下午2点，在会议室A"
  }}
]

## 注意事项
1. **上下文优先**：必须基于完整对话历史理解，不能孤立地看待单条消息
2. **指代消解**：正确处理代词、省略等语言现象，确保任务描述准确清晰
3. **信息整合**：将分散的相关信息整合到一个任务中
4. **当前日期**：截止时间请根据当前日期（{current_date}）推断
5. **输出格式**：只返回 JSON，不要包含任何其他文本或解释
6. **空结果**：如果没有找到任何任务，返回空数组 []

现在开始处理以下输入：
{chat_text}
"""


def build_context_aware_prompt(chat_text: str, current_date: str) -> str:
    """构建上下文感知的提示词模板，用于从长群聊历史中提取任务。

    该函数创建一个专门设计的提示词，指导LLM理解长群聊上下文、
    识别指代关系并提取任务。使用纯函数实现，无副作用。

    Args:
        chat_text: 长群聊历史文本，不能为空字符串或仅包含空白字符
        current_date: 当前日期字符串，格式应为 "YYYY-MM-DD"

    Returns:
        格式化后的提示词字符串

    Raises:
        TypeError: 如果chat_text或current_date不是字符串类型
        ValueError: 如果chat_text为空字符串或仅包含空白字符，
                   或者current_date不符合"YYYY-MM-DD"格式
    """
    if not isinstance(chat_text, str):
        raise TypeError(f"chat_text must be a string, got {type(chat_text).__name__}")
    
    if not isinstance(current_date, str):
        raise TypeError(f"current_date must be a string, got {type(current_date).__name__}")
    
    if not chat_text or chat_text.strip() == "":
        raise ValueError("chat_text cannot be empty or only whitespace")
    
    if len(current_date) != 10 or current_date[4] != '-' or current_date[7] != '-':
        raise ValueError(f"current_date must be in YYYY-MM-DD format, got {current_date}")
    
    try:
        year = int(current_date[0:4])
        month = int(current_date[5:7])
        day = int(current_date[8:10])
    except ValueError:
        raise ValueError(f"current_date must contain valid numeric values, got {current_date}")
    
    if not (1 <= month <= 12):
        raise ValueError(f"month must be between 1 and 12, got {month}")
    
    if not (1 <= day <= 31):
        raise ValueError(f"day must be between 1 and 31, got {day}")
    
    return CONTEXT_AWARE_EXTRACTION_PROMPT.format(
        chat_text=chat_text,
        current_date=current_date
    )

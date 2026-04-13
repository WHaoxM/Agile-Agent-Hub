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

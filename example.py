#!/usr/bin/env python3

"""
Agile-Agent Hub - 使用示例

本项目支持使用大语言模型（LLM）来智能提取聊天文本中的任务信息。
LLM 提取功能说明：
- 使用 OpenAI 兼容的 API 接口（支持 OpenAI 官方 API 或兼容的第三方服务）
- 当配置了 LLM_API_KEY 环境变量时，会优先使用 LLM 提取任务
- 如果 LLM 提取失败或未配置 API Key，会自动降级到 mock 提取模式
- 支持自定义模型、API 地址和超时时间

环境变量配置说明：
- 必需：LLM_API_KEY - 您的 LLM API 密钥
- 可选：LLM_BASE_URL - API 基础地址（默认使用 OpenAI 官方 API）
- 可选：LLM_MODEL - 模型名称（默认：gpt-3.5-turbo）
- 可选：LLM_TIMEOUT - 请求超时时间（秒，默认：30）

配置方式：
1. 创建 .env 文件，参考 .env.example
2. 或直接在运行前设置环境变量
"""

from src.pipeline import TaskPipeline


def main():
    pipeline = TaskPipeline()
    
    print("=" * 60)
    print("Agile-Agent Hub - 使用示例")
    print("=" * 60)
    print()
    
    chat_text = "@张三 明天下午3点前把API文档写好 @李四 后天上午10点前修复登录bug"
    print(f"输入聊天文本:\n{chat_text}")
    print()
    
    output = pipeline.process_chat_text(chat_text)
    
    print("=" * 60)
    print("Markdown 输出:")
    print("=" * 60)
    print(output.markdown_output)
    print()
    
    print("=" * 60)
    print("JSON 输出:")
    print("=" * 60)
    print(output.json_output)
    print()
    
    print("=" * 60)
    print(f"提取到 {len(output.tasks)} 个任务")
    print("=" * 60)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

from src.pipeline import TaskPipeline


def main():
    pipeline = TaskPipeline()
    
    print("=" * 60)
    print("Agile-Agent Hub - 自定义文本测试")
    print("=" * 60)
    print()
    
    chat_text = "任洪，把市场商业部分(营销内容和市场分析还有商品竞品这些内容完成)"
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

"""HTML 总结渲染与图片生成模块"""

import os
import tempfile
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

from .models import Task


def generate_summary_html(
    title: str,
    summary: str,
    tasks: List[Task],
    group_name: str = "",
    group_id: str = "",
    timestamp: str = "",
    message_count: int = 0,
    theme: str = "default",
    messages: List[Dict[str, Any]] = None,
    show_timeline: bool = True
) -> str:
    """生成美观的HTML总结页面。
    
    Args:
        title: 标题
        summary: 总结内容
        tasks: 任务列表
        group_name: 群名称
        group_id: 群ID
        timestamp: 时间戳
        message_count: 消息数量
        theme: 主题风格 (default, dark, colorful)
        messages: 原始消息列表，用于生成时间线
        show_timeline: 是否显示时间线
    
    Returns:
        HTML字符串
    """
    # 主题样式定义
    themes = {
        "default": {
            "bg": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "card_bg": "rgba(255, 255, 255, 0.95)",
            "text": "#333",
            "header": "#5a67d8",
            "accent": "#667eea",
            "task_bg": "#f7fafc",
            "border": "#e2e8f0"
        },
        "dark": {
            "bg": "linear-gradient(135deg, #1a202c 0%, #2d3748 100%)",
            "card_bg": "rgba(45, 55, 72, 0.95)",
            "text": "#e2e8f0",
            "header": "#63b3ed",
            "accent": "#4299e1",
            "task_bg": "#2d3748",
            "border": "#4a5568"
        },
        "colorful": {
            "bg": "linear-gradient(135deg, #f093fb 0%, #f5576c 50%, #4facfe 100%)",
            "card_bg": "rgba(255, 255, 255, 0.98)",
            "text": "#2d3748",
            "header": "#e53e3e",
            "accent": "#f5576c",
            "task_bg": "#fff5f5",
            "border": "#fed7d7"
        }
    }
    
    style = themes.get(theme, themes["default"])
    
    # 处理任务列表HTML
    tasks_html = ""
    if tasks:
        for i, task in enumerate(tasks, 1):
            assignee = task.assignee or "待分配"
            deadline = task.deadline or "待定"
            status = get_status_emoji(assignee, deadline)
            
            tasks_html += f'''
            <div class="task-item" style="
                background: {style['task_bg']};
                border-left: 4px solid {style['accent']};
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            ">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="
                        background: {style['accent']};
                        color: white;
                        width: 24px;
                        height: 24px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 12px;
                        font-weight: bold;
                        margin-right: 10px;
                    ">{i}</span>
                    <span style="font-weight: 600; color: {style['text']};">{task.task}</span>
                </div>
                <div style="display: flex; gap: 15px; font-size: 13px; color: #666; margin-left: 34px;">
                    <span>👤 {assignee}</span>
                    <span>⏰ {deadline}</span>
                    <span>{status}</span>
                </div>
            </div>
            '''
    else:
        tasks_html = f'''
        <div style="
            text-align: center;
            padding: 30px;
            color: #999;
            background: {style['task_bg']};
            border-radius: 8px;
        ">
            <div style="font-size: 48px; margin-bottom: 10px;">🎉</div>
            <div>本次会话暂无明确任务</div>
        </div>
        '''
    
    # 生成时间线 HTML
    timeline_html = ""
    if show_timeline and messages:
        timeline_items = []
        for msg in messages:
            sender_name = msg.get('sender_name', '未知用户')
            sender_id = msg.get('sender_id', '')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', 0)
            
            # 格式化时间
            if timestamp:
                msg_time = datetime.fromtimestamp(timestamp).strftime("%H:%M")
            else:
                msg_time = "--:--"
            
            # 截断过长的内容
            display_content = content[:100] + "..." if len(content) > 100 else content
            # 处理特殊字符
            display_content = display_content.replace('<', '&lt;').replace('>', '&gt;')
            
            timeline_items.append(f'''
            <div class="timeline-item" style="
                display: flex;
                gap: 12px;
                padding: 12px 0;
                border-bottom: 1px dashed {style['border']};
            ">
                <div style="
                    min-width: 50px;
                    text-align: right;
                    font-size: 12px;
                    color: #999;
                    padding-top: 2px;
                ">{msg_time}</div>
                <div style="flex: 1;">
                    <div style="
                        font-weight: 600;
                        font-size: 13px;
                        color: {style['header']};
                        margin-bottom: 4px;
                    ">{sender_name}</div>
                    <div style="
                        font-size: 14px;
                        color: {style['text']};
                        line-height: 1.5;
                        word-break: break-word;
                    ">{display_content}</div>
                </div>
            </div>
            ''')
        
        if timeline_items:
            timeline_html = f'''
            <div class="section">
                <div class="section-title">💬 会话时间线 ({len(messages)} 条消息)</div>
                <div style="
                    background: {style['card_bg']};
                    border-radius: 12px;
                    padding: 15px 20px;
                    border: 1px solid {style['border']};
                    max-height: 400px;
                    overflow-y: auto;
                ">
                    {''.join(timeline_items)}
                </div>
            </div>
            '''
    
    # 统计信息
    stats_html = ""
    if message_count > 0:
        stats_html = f'''
        <div style="
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        ">
            <div style="
                background: rgba(255,255,255,0.2);
                padding: 10px 20px;
                border-radius: 20px;
                font-size: 13px;
            ">
                💬 {message_count} 条消息
            </div>
            <div style="
                background: rgba(255,255,255,0.2);
                padding: 10px 20px;
                border-radius: 20px;
                font-size: 13px;
            ">
                📋 {len(tasks)} 个任务
            </div>
        </div>
        '''
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
            background: {style['bg']};
            min-height: 100vh;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: {style['card_bg']};
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: {style['header']};
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 8px;
        }}
        .header .meta {{
            font-size: 13px;
            opacity: 0.9;
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 25px;
        }}
        .section-title {{
            font-size: 16px;
            font-weight: 700;
            color: {style['header']};
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .summary-text {{
            background: {style['task_bg']};
            padding: 20px;
            border-radius: 12px;
            line-height: 1.8;
            color: {style['text']};
            font-size: 14px;
            border: 1px solid {style['border']};
        }}
        .footer {{
            background: rgba(0,0,0,0.03);
            padding: 20px 30px;
            text-align: center;
            font-size: 12px;
            color: #999;
            border-top: 1px solid {style['border']};
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            {stats_html}
            <h1>📊 {title}</h1>
            <div class="meta">
                {f'群: {group_name}' if group_name else f'群号: {group_id}'} · {timestamp}
            </div>
        </div>
        
        <div class="content">
            <div class="section">
                <div class="section-title">📝 会话总结</div>
                <div class="summary-text">{summary.replace(chr(10), '<br>')}</div>
            </div>
            
            <div class="section">
                <div class="section-title">📋 任务清单 ({len(tasks)})</div>
                {tasks_html}
            </div>
            
            {timeline_html}
        </div>
        
        <div class="footer">
            Powered by Agile Agent Hub · AI 智能提取
        </div>
    </div>
</body>
</html>'''
    
    return html


def get_status_emoji(assignee: str, deadline: str) -> str:
    """根据负责人和截止日期返回状态表情。"""
    if assignee == "待分配":
        return "⚪ 待分配"
    if deadline == "待定":
        return "🟡 待确认时间"
    
    try:
        # 简单判断截止日期是否临近
        if "今天" in deadline or "明天" in deadline:
            return "🔴 紧急"
        return "🟢 进行中"
    except:
        return "⚪ 待处理"


async def html_to_image(
    html_content: str,
    output_path: Optional[str] = None,
    width: int = 640,
    height: Optional[int] = None,
    full_page: bool = True
) -> Optional[str]:
    """将HTML转换为图片。
    
    Args:
        html_content: HTML内容
        output_path: 输出路径，None则使用临时文件
        width: 视口宽度
        height: 视口高度，None则自动
        full_page: 是否截取完整页面
    
    Returns:
        图片文件路径，失败返回None
    """
    if not HAS_PLAYWRIGHT:
        print("[WARN] Playwright 未安装，无法生成图片。请运行: pip install playwright && playwright install chromium")
        return None
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={'width': width, 'height': height or 800})
            
            # 加载HTML
            await page.set_content(html_content, wait_until='networkidle')
            
            # 等待字体加载
            await page.wait_for_timeout(1000)
            
            # 确定输出路径
            if output_path is None:
                output_path = os.path.join(tempfile.gettempdir(), f'summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
            
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # 截图
            await page.screenshot(path=output_path, full_page=full_page)
            
            await browser.close()
            
            return output_path
            
    except Exception as e:
        print(f"[ERROR] HTML转图片失败: {e}")
        return None


async def generate_summary_image(
    title: str,
    summary: str,
    tasks: List[Task],
    group_name: str = "",
    group_id: str = "",
    output_path: Optional[str] = None,
    theme: str = "colorful",
    messages: List[Dict[str, Any]] = None,
    show_timeline: bool = True
) -> Optional[str]:
    """一站式生成总结图片。
    
    Args:
        title: 标题
        summary: 总结内容
        tasks: 任务列表
        group_name: 群名称
        group_id: 群ID
        output_path: 输出路径
        theme: 主题
        messages: 原始消息列表
        show_timeline: 是否显示时间线
    
    Returns:
        图片路径或None
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    html = generate_summary_html(
        title=title,
        summary=summary,
        tasks=tasks,
        group_name=group_name,
        group_id=group_id,
        timestamp=timestamp,
        theme=theme,
        messages=messages,
        show_timeline=show_timeline
    )
    
    return await html_to_image(html, output_path)

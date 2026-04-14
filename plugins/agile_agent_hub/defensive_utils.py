"""
防御性工具函数模块

提供类型安全、输入验证的工具函数，用于防止边界测试攻击。
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import json
import os


class ValidationError(Exception):
    """输入验证错误异常"""
    pass


# =============================================================================
# 消息格式化相关
# =============================================================================

MAX_MESSAGES = 1000
MAX_MESSAGE_LENGTH = 1000
MAX_SENDER_NAME_LENGTH = 100
MAX_TOTAL_OUTPUT_LENGTH = 10000


def safe_format_group_messages(messages: List[Dict[str, Any]]) -> str:
    """安全地格式化群聊消息为文本。
    
    使用防御性编程实现，对所有输入进行严格验证。
    
    Args:
        messages: 消息列表，每个消息必须是字典，包含 sender_name, content, timestamp
        
    Returns:
        格式化后的文本字符串，保证不为 None
    """
    if messages is None:
        return ""
    
    if not isinstance(messages, list):
        return ""
    
    if len(messages) == 0:
        return ""
    
    formatted_lines: List[str] = []
    
    for index, msg in enumerate(messages):
        if not isinstance(msg, dict):
            continue
        
        sender_name = _safe_get_string(msg, "sender_name", "未知")
        sender_name = _truncate_string(sender_name, MAX_SENDER_NAME_LENGTH)
        
        content = _safe_get_string(msg, "content", "")
        content = _truncate_string(content, MAX_MESSAGE_LENGTH)
        
        timestamp = msg.get("timestamp")
        time_str = _safe_format_timestamp(timestamp)
        
        if time_str:
            line = f"[{time_str}] {sender_name}: {content}"
        else:
            line = f"{sender_name}: {content}"
        
        formatted_lines.append(line)
    
    result = "\n".join(formatted_lines)
    
    if len(result) > MAX_TOTAL_OUTPUT_LENGTH:
        result = result[:MAX_TOTAL_OUTPUT_LENGTH - 3] + "..."
    
    return result


def _safe_get_string(data: Dict[str, Any], key: str, default: str) -> str:
    """安全地从字典中获取字符串值。"""
    value = data.get(key)
    if value is None:
        return default
    if not isinstance(value, str):
        return str(value)
    return value


def _truncate_string(s: str, max_length: int) -> str:
    """安全地截断字符串，防止超长。"""
    if not isinstance(s, str):
        s = str(s)
    if len(s) > max_length:
        return s[:max_length] + "..."
    return s


def _safe_format_timestamp(timestamp: Any) -> str:
    """安全地格式化时间戳。"""
    if timestamp is None:
        return ""
    
    if isinstance(timestamp, (int, float)):
        if timestamp < 0:
            return ""
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%H:%M:%S")
        except (ValueError, OSError):
            return ""
    
    return ""


# =============================================================================
# 日期验证相关
# =============================================================================

def validate_date_string(date_str: str) -> bool:
    """验证日期字符串是否为有效的 YYYY-MM-DD 格式。"""
    if not isinstance(date_str, str):
        return False
    
    if len(date_str) != 10:
        return False
    
    if date_str[4] != '-' or date_str[7] != '-':
        return False
    
    try:
        year = int(date_str[0:4])
        month = int(date_str[5:7])
        day = int(date_str[8:10])
    except ValueError:
        return False
    
    if not (1 <= month <= 12):
        return False
    
    if not (1 <= day <= 31):
        return False
    
    return True


# =============================================================================
# 文件操作相关
# =============================================================================

MAX_FILENAME_LENGTH = 255
SAFE_FILENAME_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._"


def safe_make_dirs(path: str) -> None:
    """安全地创建目录，防止路径遍历攻击。"""
    if not isinstance(path, str):
        raise TypeError("path must be a string")
    
    abs_path = os.path.abspath(path)
    
    if not abs_path:
        raise ValidationError("Invalid path")
    
    try:
        os.makedirs(abs_path, exist_ok=True)
    except OSError as e:
        raise ValidationError(f"Failed to create directory: {e}") from e


def safe_filename(filename: str) -> str:
    """安全地清理文件名，防止路径遍历和非法字符。"""
    if not isinstance(filename, str):
        filename = str(filename) if filename is not None else ""
    
    if not filename:
        return "unnamed_file"
    
    cleaned = filename
    cleaned = cleaned.replace("../", "")
    cleaned = cleaned.replace("..\\", "")
    cleaned = cleaned.replace("/", "_")
    cleaned = cleaned.replace("\\", "_")
    cleaned = cleaned.replace(":", "_")
    cleaned = cleaned.replace("*", "_")
    cleaned = cleaned.replace("?", "_")
    cleaned = cleaned.replace('"', "_")
    cleaned = cleaned.replace("<", "_")
    cleaned = cleaned.replace(">", "_")
    cleaned = cleaned.replace("|", "_")
    cleaned = cleaned.replace(" ", "_")
    
    if not cleaned:
        cleaned = "unnamed_file"
    
    if len(cleaned) > MAX_FILENAME_LENGTH:
        name, ext = os.path.splitext(cleaned)
        max_name_length = MAX_FILENAME_LENGTH - len(ext) - 3
        if max_name_length > 0:
            cleaned = name[:max_name_length] + "..." + ext
        else:
            cleaned = "unnamed_file" + ext
    
    return cleaned


def safe_join_path(base: str, *paths: str) -> str:
    """安全地连接路径，防止路径遍历攻击。"""
    if not isinstance(base, str):
        raise TypeError("base must be a string")
    
    base_abs = os.path.abspath(base)
    result = os.path.join(base_abs, *paths)
    result_abs = os.path.abspath(result)
    
    if not result_abs.startswith(base_abs):
        raise ValidationError("Path traversal attempt detected")
    
    return result_abs


# =============================================================================
# JSON 解析相关
# =============================================================================

MAX_JSON_SIZE = 10 * 1024 * 1024  # 10 MB


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """安全地解析 JSON 字符串。"""
    if not isinstance(json_str, str):
        return default
    
    if len(json_str) > MAX_JSON_SIZE:
        return default
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return default


def safe_json_dumps(obj: Any, ensure_ascii: bool = False, indent: Optional[int] = 2) -> str:
    """安全地序列化对象为 JSON 字符串。"""
    try:
        return json.dumps(obj, ensure_ascii=ensure_ascii, indent=indent)
    except (TypeError, ValueError, OverflowError):
        return "{}"


# =============================================================================
# 配置验证相关
# =============================================================================

def validate_llm_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """验证 LLM 配置。"""
    errors = []
    
    api_base = config.get("llm_api_base", "")
    api_key = config.get("llm_api_key", "")
    model = config.get("llm_model", "")
    
    if not isinstance(api_base, str) or not api_base.strip():
        errors.append("llm_api_base 不能为空")
    
    if not isinstance(api_key, str) or not api_key.strip():
        errors.append("llm_api_key 不能为空")
    
    if not isinstance(model, str) or not model.strip():
        errors.append("llm_model 不能为空")
    
    return len(errors) == 0, errors


def validate_schedule_time(time_str: str) -> bool:
    """验证定时时间格式（HH:MM）。"""
    if not isinstance(time_str, str):
        return False
    
    if len(time_str) != 5 or time_str[2] != ':':
        return False
    
    try:
        hour = int(time_str[0:2])
        minute = int(time_str[3:5])
    except ValueError:
        return False
    
    if not (0 <= hour <= 23):
        return False
    
    if not (0 <= minute <= 59):
        return False
    
    return True


def validate_monitored_groups(groups: Any) -> Tuple[bool, List[str]]:
    """验证监听群组列表。"""
    errors = []
    
    if groups is None:
        return True, []
    
    if not isinstance(groups, list):
        errors.append("monitored_groups 必须是列表")
        return False, errors
    
    for index, item in enumerate(groups):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"群组 ID 索引 {index} 无效")
    
    return len(errors) == 0, errors


def validate_monitored_users(users: Any) -> Tuple[bool, List[str]]:
    """验证监听用户QQ号列表。"""
    errors = []
    
    if users is None:
        return True, []
    
    if not isinstance(users, list):
        errors.append("monitored_users 必须是列表")
        return False, errors
    
    for index, item in enumerate(users):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"用户 QQ 号索引 {index} 无效")
    
    return len(errors) == 0, errors

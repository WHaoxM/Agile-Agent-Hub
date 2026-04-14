"""插件入口。"""

import asyncio
import json
import os
import openai
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any, Optional
from ncatbot.plugin import NcatBotPlugin
from ncatbot.core import registrar
from .models import Task
from .llm_client import call_llm_for_group_chat_summary, LLMClientError
from .parser import parse_llm_response, TaskParseError
from .defensive_utils import (
    safe_format_group_messages,
    safe_json_loads,
    safe_json_dumps,
    safe_make_dirs,
    safe_filename,
    safe_join_path,
    validate_date_string,
    validate_llm_config,
    validate_schedule_time,
    validate_monitored_groups,
    validate_monitored_users
)
from .html_renderer import generate_summary_image, HAS_PLAYWRIGHT


class AgileAgentHub(NcatBotPlugin):
    """Agile Agent Hub 插件。

    注意：插件元数据由 manifest.toml 提供，不要在类中声明。
    """

    async def on_load(self):
        self.init_defaults()
        self.logger.info(f"{self.name} 已加载")
        
        self.logger.info("配置信息:")
        self.logger.info(f"  schedule_time: {self.config.get('schedule_time', '08:00')}")
        self.logger.info(f"  monitored_groups: {self.config.get('monitored_groups', [])}")
        self.logger.info(f"  llm_api_base: {self.config.get('llm_api_base', 'https://api.openai.com/v1')}")
        self.logger.info(f"  llm_model: {self.config.get('llm_model', 'gpt-4o')}")
        self.logger.info(f"  send_to_group: {self.config.get('send_to_group', False)}")
        self.logger.info(f"  summary_output_dir: {self.config.get('summary_output_dir', 'summaries')}")
        
        self.logger.info("开始验证配置...")
        
        schedule_time = self.config.get("schedule_time", "08:00")
        if not validate_schedule_time(schedule_time):
            self.logger.warning(f"⚠️  定时时间格式无效: {schedule_time}，使用默认值 08:00")
            self.config["schedule_time"] = "08:00"
            schedule_time = "08:00"
        
        monitored_groups = self.config.get("monitored_groups", [])
        is_valid, errors = validate_monitored_groups(monitored_groups)
        if not is_valid:
            self.logger.warning(f"⚠️  监听群组配置无效: {errors}")
        
        monitored_users = self.config.get("monitored_users", [])
        is_valid, errors = validate_monitored_users(monitored_users)
        if not is_valid:
            self.logger.warning(f"⚠️  监听用户配置无效: {errors}")
        
        monitored_private_users = self.config.get("monitored_private_users", [])
        is_valid, errors = validate_monitored_users(monitored_private_users)
        if not is_valid:
            self.logger.warning(f"⚠️  私聊监听用户配置无效: {errors}")
        
        is_valid, errors = validate_llm_config(self.config)
        if not is_valid:
            self.logger.warning(f"⚠️  LLM 配置无效: {errors}")
        
        self.logger.info("配置验证完成")
        
        if monitored_groups:
            self.logger.info(f"📋 监听群组: {monitored_groups}")
        else:
            self.logger.info("📋 监听所有群组（monitored_groups 为空）")
        
        if monitored_users:
            self.logger.info(f"👤 只监听指定用户: {monitored_users}")
        else:
            self.logger.info("👤 监听所有用户（monitored_users 为空）")
        
        # 发送配置
        send_to_group = self.config.get("send_to_group", False)
        summary_target_groups = self.config.get("summary_target_groups", [])
        if send_to_group:
            if summary_target_groups:
                self.logger.info(f"📤 总结将发送到指定群: {summary_target_groups}")
            else:
                self.logger.info("📤 总结将发送到原群组（summary_target_groups 为空）")
        else:
            self.logger.info("📤 不发送总结到群内（send_to_group: false）")

        # 发送配置
        dynamic_summary_enabled = self.config.get("dynamic_summary_enabled", False)
        dynamic_summary_idle = self.config.get("dynamic_summary_idle_minutes", 10)
        if dynamic_summary_enabled:
            self.logger.info(f"⚡ 动态总结已启用: 空闲 {dynamic_summary_idle} 分钟后自动总结")
        else:
            self.logger.info("⚡ 动态总结已禁用")
        
        # 分身功能配置
        avatar_enabled = self.config.get("avatar_enabled", False)
        if avatar_enabled:
            self.logger.info("🎭 分身自动回复已启用")
        else:
            self.logger.info("🎭 分身自动回复已禁用")
        
        # 图片总结配置
        summary_as_image = self.config.get("summary_as_image", True)
        if summary_as_image:
            if HAS_PLAYWRIGHT:
                theme = self.config.get("summary_image_theme", "colorful")
                self.logger.info(f"🖼️  总结将以图片形式发送，主题: {theme}")
            else:
                self.logger.warning("🖼️  图片总结已启用但 Playwright 未安装，请运行: pip install playwright && playwright install chromium")
        else:
            self.logger.info("📝 总结将以文本形式发送")

        # 启动消息监听协程
        self.logger.info("🎧 启动群消息监听协程...")
        self._msg_listener_task = asyncio.create_task(self._group_message_listener())
        self._private_listener_task = asyncio.create_task(self._private_message_listener())
        
        # 启动动态总结后台协程
        if dynamic_summary_enabled:
            self._dynamic_summary_task = asyncio.create_task(self._dynamic_summary_loop())
        
        # 启动私聊回复队列处理协程（支持所有人按顺序回复）
        if avatar_enabled:
            self._avatar_reply_task = asyncio.create_task(self._avatar_reply_queue_loop())
            self.logger.info("🎭 私聊回复队列系统已启动（支持所有人，按顺序回复）")

        self.add_scheduled_task(
            name="daily_summary",
            interval=schedule_time
        )
        self.logger.info(f"定时任务已注册: daily_summary 于 {schedule_time}")

    def init_defaults(self):
        defaults = {
            "schedule_time": "08:00",
            "monitored_groups": [],
            "monitored_users": [],
            "monitored_private_users": [],
            "llm_api_base": "https://api.openai.com/v1",
            "llm_api_key": "",
            "llm_model": "gpt-4o",
            "send_to_group": False,
            "summary_target_groups": [],
            "summary_output_dir": "summaries",
            "dynamic_summary_enabled": False,
            "dynamic_summary_idle_minutes": 10,
            "dynamic_summary_min_messages": 5,
            "summary_as_image": True,
            "summary_image_theme": "colorful"
        }
        for key, value in defaults.items():
            if key not in self.config:
                self.config[key] = value
        
        if not hasattr(self, 'data'):
            self.data = {"messages": {}}
        
        # 动态总结状态跟踪
        self._last_message_time: Dict[str, float] = {}
        self._dynamic_summary_task: Optional[asyncio.Task] = None
        self._summary_lock: asyncio.Lock = asyncio.Lock()
        
        # 私聊回复队列系统（支持所有人按顺序回复）
        self._avatar_reply_queue: asyncio.Queue = asyncio.Queue()
        self._avatar_reply_task: Optional[asyncio.Task] = None
        self._avatar_reply_lock: asyncio.Lock = asyncio.Lock()
        self._pending_replies: Dict[str, Dict[str, Any]] = {}
        
        # 智能分身控制系统：用户手动回复检测与学习
        self._manual_reply_cache: Dict[str, Dict[str, Any]] = {}  # user_id -> {last_manual_time, samples, is_active}
        self._avatar_learning_samples: Dict[str, List[str]] = {}  # user_id -> 用户回复样本
        self._avatar_active_sessions: set = set()  # 记录分身已激活的对话对象（user_id）
        self.MANUAL_REPLY_COOLDOWN = 300  # 5分钟冷却时间（秒）
        self.MAX_LEARNING_SAMPLES = 10  # 最大学习样本数

    async def _group_message_listener(self):
        """通过事件流监听群消息。"""
        self.logger.info("🎧 群消息监听协程已启动")
        try:
            async with self.events("message.group") as stream:
                async for event in stream:
                    try:
                        await self.handle_group_message(event)
                    except Exception as e:
                        self.logger.error(f"处理群消息异常: {e}", exc_info=True)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"群消息监听异常: {e}", exc_info=True)

    async def _private_message_listener(self):
        """通过事件流监听私聊消息。"""
        monitored_private_users = self.config.get("monitored_private_users", [])
        avatar_enabled = self.config.get("avatar_enabled", False)
        avatar_target_users = self.config.get("avatar_target_users", [])
        
        # 检查是否需要监听私聊
        reply_mode = self.config.get("avatar_reply_mode", "all")
        need_private_listen = bool(monitored_private_users) or (avatar_enabled and (reply_mode == "all" or bool(avatar_target_users)))
        
        if not need_private_listen:
            self.logger.info("👤 不监听私聊消息（monitored_private_users 为空且未启用分身）")
            return
        
        reply_mode = self.config.get("avatar_reply_mode", "all")
        
        if monitored_private_users:
            self.logger.info(f"👤 开始监听私聊消息，只监听用户: {monitored_private_users}")
        elif avatar_enabled:
            if reply_mode == "all":
                self.logger.info(f"👤 开始监听私聊消息（分身模式: 所有人）")
            elif reply_mode == "target" and avatar_target_users:
                self.logger.info(f"👤 开始监听私聊消息（分身模式: 指定对象 {avatar_target_users}）")
        
        try:
            async with self.events("message.private") as stream:
                async for event in stream:
                    try:
                        await self.handle_private_message(event)
                    except Exception as e:
                        self.logger.error(f"处理私聊消息异常: {e}", exc_info=True)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"私聊消息监听异常: {e}", exc_info=True)

    async def handle_group_message(self, event):
        self.logger.info(f"[DEBUG] 进入 handle_group_message, event type: {type(event)}, has data: {hasattr(event, 'data')}")
        data = event.data
        group_id = str(data.group_id)
        sender_id = str(data.user_id)
        sender_name = getattr(data.sender, 'nickname', '') or getattr(data.sender, 'card', '') or str(sender_id)
        content = data.raw_message
        timestamp = getattr(data, 'time', int(datetime.now().timestamp()))
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        monitored_groups = self.config.get("monitored_groups", [])
        
        # 过滤非监听群
        if monitored_groups and group_id not in monitored_groups:
            self.logger.debug(f"[SKIP] 跳过非监听群: {group_id}")
            return
        
        monitored_users = self.config.get("monitored_users", [])
        if monitored_users and sender_id not in monitored_users:
            return
        
        self.logger.info(f"收到群消息 - 群组: {group_id}, 发送者: {sender_name} ({sender_id})")
        self.logger.info(f"原始内容: {repr(content)}")
        
        # 检测是否是自己发的消息（避免自循环）
        bot_uin = getattr(self, 'bot_uin', None)
        if bot_uin and sender_id == str(bot_uin):
            self.logger.info(f"[SELF] 检测到 Bot 自己发的消息，跳过处理")
            # 但仍然处理 !总结 命令（允许自己触发）
            pass
        
        # 检测 !总结 命令（支持多种格式）
        content_clean = content.strip()
        # 去除可能的引用回复前缀 [CQ:reply...]
        if "[CQ:" in content_clean:
            import re
            content_clean = re.sub(r'\[CQ:[^\]]+\]', '', content_clean).strip()
        
        self.logger.info(f"清理后内容: {repr(content_clean)}")
        
        if content_clean == "!总结":
            self.logger.info(f"🎯 检测到 !总结 命令，群: {group_id}，发送者: {sender_id}")
            # 在后台触发即时总结（不阻塞消息处理）
            asyncio.create_task(self._trigger_instant_summary(group_id, sender_id, sender_name))
            return
        
        if "messages" not in self.data:
            self.data["messages"] = {}
        if today not in self.data["messages"]:
            self.data["messages"][today] = {}
        if group_id not in self.data["messages"][today]:
            self.data["messages"][today][group_id] = []
        
        self.data["messages"][today][group_id].append({
            "sender_id": sender_id,
            "sender_name": sender_name,
            "content": content,
            "timestamp": timestamp,
            "source": "group"
        })
        
        # 更新最后消息时间（用于动态总结）
        if self.config.get("dynamic_summary_enabled", False):
            self._last_message_time[group_id] = asyncio.get_event_loop().time()

    async def handle_private_message(self, event):
        """处理私聊消息。"""
        data = event.data
        sender_id = str(data.user_id)
        sender_name = getattr(data.sender, 'nickname', '') or str(sender_id)
        content = data.raw_message
        timestamp = getattr(data, 'time', int(datetime.now().timestamp()))
        
        self.logger.info(f"[私聊调试] 收到消息 - 发送者: {sender_name} ({sender_id}), 内容: {content[:30]}...")
        
        monitored_private_users = self.config.get("monitored_private_users", [])
        self.logger.info(f"[私聊调试] monitored_private_users: {monitored_private_users}, 是否过滤: {monitored_private_users and sender_id not in monitored_private_users}")
        
        if monitored_private_users and sender_id not in monitored_private_users:
            self.logger.info(f"[私聊调试] 发送者 {sender_id} 不在监听列表，跳过")
            return
        
        self.logger.info(f"[私聊调试] 发送者 {sender_id} 通过过滤，继续处理")
        
        # 检测私聊中的 !总结 命令
        content_clean = content.strip()
        if content_clean == "!总结":
            self.logger.info(f"🎯 私聊检测到 !总结 命令，发送者: {sender_id}")
            # 私聊触发总结 - 需要指定群号
            await self.api.platform("qq").post_private_msg(
                user_id=sender_id,
                text="📋 请指定要总结的群号，格式：!总结 群号\n例如：!总结 2168061868"
            )
            return
        
        # 检测 "!总结 群号" 格式
        if content_clean.startswith("!总结 "):
            parts = content_clean.split()
            if len(parts) >= 2:
                target_group = parts[1]
                self.logger.info(f"🎯 私聊触发群 {target_group} 的总结，发送者: {sender_id}")
                # 回复确认
                await self.api.platform("qq").post_private_msg(
                    user_id=sender_id,
                    text=f"🤖 正在生成群 {target_group} 的总结..."
                )
                # 触发总结
                today = datetime.now().strftime("%Y-%m-%d")
                messages = []
                if "messages" in self.data and today in self.data["messages"]:
                    messages = self.data["messages"][today].get(target_group, [])
                
                if not messages:
                    await self.api.platform("qq").post_private_msg(
                        user_id=sender_id,
                        text=f"📭 群 {target_group} 今天还没有消息记录"
                    )
                    return
                
                await self._trigger_instant_summary(target_group, sender_id, sender_name)
                await self.api.platform("qq").post_private_msg(
                    user_id=sender_id,
                    text=f"✅ 群 {target_group} 的总结已生成并发送！"
                )
                return
        
        # 确定存储key：统一用对方QQ作为key
        bot_uin = str(self.config.get("bot_uin", ""))
        if sender_id == bot_uin:
            # 用户手动回复，需要从上下文中找到对方QQ
            target_user_id = self._find_target_user_from_context(today)
            if not target_user_id:
                # 如果找不到对方（比如是新会话），使用一个临时key
                target_user_id = sender_id  #  Fallback，但这种情况不应该发生
            storage_key = f"private_{target_user_id}"
            
            # 检查是否值得学习：分身已激活 或 正在冷却中
            is_avatar_active = target_user_id in self._avatar_active_sessions
            is_cooling_down = self._is_avatar_cooling_down(target_user_id)
            
            if is_avatar_active or is_cooling_down:
                # 这是分身介入后的用户手动回复，值得学习
                await self._record_manual_reply(storage_key, content)
                status = "已激活" if is_avatar_active else "冷却中"
                self.logger.info(f"🎭 检测到用户手动回复给 {target_user_id}（分身{status}），记录样本并延长冷却")
                # 刷新冷却时间
                self._refresh_cooldown(target_user_id)
                # 从激活集合移除
                self._avatar_active_sessions.discard(target_user_id)
            else:
                self.logger.debug(f"🎭 用户手动回复给 {target_user_id}（分身未激活），不记录样本")
                
            # 存储消息（使用对方QQ作为key）
            today = datetime.now().strftime("%Y-%m-%d")
            if "messages" not in self.data:
                self.data["messages"] = {}
            if today not in self.data["messages"]:
                self.data["messages"][today] = {}
            if storage_key not in self.data["messages"][today]:
                self.data["messages"][today][storage_key] = []
            
            self.data["messages"][today][storage_key].append({
                "sender_id": sender_id,
                "sender_name": sender_name,
                "content": content,
                "timestamp": timestamp,
                "source": "private"
            })
            return  # 不触发分身回复
        else:
            # 对方发的消息，直接用对方QQ作为key
            storage_key = f"private_{sender_id}"
            
            today = datetime.now().strftime("%Y-%m-%d")
            if "messages" not in self.data:
                self.data["messages"] = {}
            if today not in self.data["messages"]:
                self.data["messages"][today] = {}
            if storage_key not in self.data["messages"][today]:
                self.data["messages"][today][storage_key] = []
            
            self.data["messages"][today][storage_key].append({
                "sender_id": sender_id,
                "sender_name": sender_name,
                "content": content,
                "timestamp": timestamp,
                "source": "private"
            })
            
            # AI 分身自动回复
            await self._handle_avatar_reply(sender_id, sender_name, content)

    async def _handle_avatar_reply(self, sender_id: str, sender_name: str, content: str):
        """AI 分身自动回复处理 - 将消息加入队列等待处理。"""
        # 检查分身功能是否启用
        if not self.config.get("avatar_enabled", False):
            return
        
        # 防止自循环：Bot 自己发的消息不回复
        bot_uin = str(self.config.get("bot_uin", ""))
        if sender_id == bot_uin:
            self.logger.debug(f"🎭 跳过 Bot 自己的消息: {sender_id}")
            return
        
        # 检查冷却期：用户最近是否手动回复过
        if self._is_avatar_cooling_down(sender_id):
            return  # 冷却期内，分身不回复
        
        # 检查回复模式
        reply_mode = self.config.get("avatar_reply_mode", "all")
        avatar_target_users = self.config.get("avatar_target_users", [])
        
        if reply_mode == "target" and avatar_target_users:
            # target 模式：只回复指定对象
            if sender_id not in avatar_target_users:
                return
        
        # 将消息加入队列
        await self._avatar_reply_queue.put({
            'sender_id': sender_id,
            'sender_name': sender_name,
            'content': content
        })
        
        # 标记该会话分身已激活（用于后续学习判断）
        self._avatar_active_sessions.add(sender_id)
        
        mode_text = "所有人" if reply_mode == "all" else "指定对象"
        self.logger.info(f"🎭 消息已加入队列 - {sender_name} ({sender_id}), 当前队列: {self._avatar_reply_queue.qsize()}, 模式: {mode_text}")

    async def _record_manual_reply(self, private_key: str, content: str):
        """记录用户手动回复，用于学习风格和暂停分身。"""
        now = asyncio.get_event_loop().time()
        
        # 更新手动回复缓存
        if private_key not in self._manual_reply_cache:
            self._manual_reply_cache[private_key] = {
                "last_manual_time": now,
                "sample_count": 0
            }
        else:
            self._manual_reply_cache[private_key]["last_manual_time"] = now
            self._manual_reply_cache[private_key]["sample_count"] += 1
        
        # 收集学习样本
        user_id = private_key.replace("private_", "")
        if user_id not in self._avatar_learning_samples:
            self._avatar_learning_samples[user_id] = []
        
        # 添加样本，限制数量
        self._avatar_learning_samples[user_id].append(content)
        if len(self._avatar_learning_samples[user_id]) > self.MAX_LEARNING_SAMPLES:
            removed = self._avatar_learning_samples[user_id].pop(0)  # 移除最旧的
            self.logger.debug(f"🎭 样本库已满，移除最旧样本: {removed[:30]}...")
        
        # 显示所有已记录的样本
        samples_preview = " | ".join([f"{i+1}.{s[:20]}..." for i, s in enumerate(self._avatar_learning_samples[user_id][-3:])])
        self.logger.info(f"🎭 ✅ 记录学习样本 [{private_key}] 第{len(self._avatar_learning_samples[user_id])}条: \"{content[:50]}...\" | 最近3条: {samples_preview}")
    
    def _find_target_user_from_context(self, today: str) -> Optional[str]:
        """找到最近活跃的对方QQ号。
        
        从今天的私聊会话中，找到最近有消息的对方（非bot）。
        用于确定用户手动回复的目标对象。
        """
        if "messages" not in self.data or today not in self.data["messages"]:
            return None
        
        bot_uin = str(self.config.get("bot_uin", ""))
        
        # 找到最近有消息的会话（对方发的消息）
        latest_time = 0
        target_user_id = None
        
        for private_key, messages in self.data["messages"][today].items():
            if not private_key.startswith("private_"):
                continue
            
            user_id = private_key.replace("private_", "")
            if user_id == bot_uin:
                continue  # 跳过bot自己的key
            
            # 检查这个会话最近是否有消息
            if messages:
                last_msg_time = messages[-1].get("timestamp", 0)
                if last_msg_time > latest_time:
                    latest_time = last_msg_time
                    target_user_id = user_id
        
        return target_user_id
    
    def _refresh_cooldown(self, sender_id: str):
        """刷新冷却期时间。"""
        private_key = f"private_{sender_id}"
        if private_key in self._manual_reply_cache:
            self._manual_reply_cache[private_key]["last_manual_time"] = asyncio.get_event_loop().time()
            self.logger.info(f"🎭 刷新冷却期 - {private_key}")
    
    def _is_avatar_cooling_down(self, sender_id: str) -> bool:
        """检查分身是否处于冷却期（用户最近手动回复过）。"""
        private_key = f"private_{sender_id}"
        
        if private_key not in self._manual_reply_cache:
            return False  # 没有记录，可以回复
        
        last_manual_time = self._manual_reply_cache[private_key].get("last_manual_time", 0)
        now = asyncio.get_event_loop().time()
        elapsed = now - last_manual_time
        
        if elapsed < self.MANUAL_REPLY_COOLDOWN:
            remaining = self.MANUAL_REPLY_COOLDOWN - elapsed
            self.logger.info(f"🎭 分身冷却中 - {private_key} 还需 {remaining:.0f} 秒")
            return True  # 仍在冷却期
        
        return False  # 冷却期已过
    
    async def _generate_learned_prompt(self, base_prompt: str, user_id: str) -> str:
        """基于用户样本生成学习后的增强提示词。"""
        samples = self._avatar_learning_samples.get(user_id, [])
        
        if not samples:
            return base_prompt
        
        # 如果样本足够，用LLM分析用户风格
        if len(samples) >= 3:
            try:
                api_base = self.config.get("llm_api_base", "")
                api_key = self.config.get("llm_api_key", "")
                model = self.config.get("llm_model", "")
                
                samples_text = "\n".join([f"- {s}" for s in samples[-5:]])
                
                analyze_prompt = f"""分析以下用户的回复样本，总结其语气特点、常用表达方式、标点习惯、表情使用风格等：

用户回复样本：
{samples_text}

请用2-3句话概括这位用户的回复风格特点："""
                
                client_kwargs = {
                    "api_key": api_key,
                    "timeout": 10
                }
                if api_base:
                    client_kwargs["base_url"] = api_base
                
                client = openai.OpenAI(**client_kwargs)
                
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "你是一个语气分析助手，请分析用户的表达风格。"},
                        {"role": "user", "content": analyze_prompt}
                    ],
                    temperature=0.5,
                    max_tokens=150
                )
                
                if response.choices and response.choices[0].message.content:
                    style_analysis = response.choices[0].message.content.strip()
                    
                    # 构建增强提示词
                    enhanced_prompt = f"""{base_prompt}

【风格学习】参考你平时的回复习惯：{style_analysis}
请继续保持这种自然、个性化的表达方式。"""
                    
                    self.logger.info(f"🎭 已为用户 {user_id} 生成风格增强提示词")
                    return enhanced_prompt
                    
            except Exception as e:
                self.logger.warning(f"🎭 风格学习失败: {e}")
        
        return base_prompt

    async def _compress_conversation(self, history: str, avatar_prompt: str) -> str:
        """用LLM压缩早期对话历史，提取关键信息。"""
        try:
            api_base = self.config.get("llm_api_base", "")
            api_key = self.config.get("llm_api_key", "")
            model = self.config.get("llm_model", "")
            
            compress_prompt = f"""请压缩以下对话历史，提取关键信息（讨论的主题、达成的共识、未解决的问题等），用2-3句话概括：

{history}"""
            
            client_kwargs = {
                "api_key": api_key,
                "timeout": 10
            }
            if api_base:
                client_kwargs["base_url"] = api_base
            
            client = openai.OpenAI(**client_kwargs)
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个对话摘要助手，请简洁概括对话要点。"},
                    {"role": "user", "content": compress_prompt}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
            return ""
        except Exception as e:
            self.logger.warning(f"🎭 压缩对话历史失败: {e}")
            return "(历史对话较长，已省略早期记录)"

    def format_group_messages(self, messages: List[dict]) -> str:
        """格式化群聊消息为文本（使用防御性工具函数）。

        Args:
            messages: 消息列表，每个消息包含 sender_name, content, timestamp

        Returns:
            格式化后的文本字符串
        """
        return safe_format_group_messages(messages)

    async def call_llm_and_extract_tasks(self, chat_text: str) -> Tuple[str, str, List[Task]]:
        """调用 LLM 生成总结和提取任务。

        Args:
            chat_text: 格式化后的群聊文本

        Returns:
            元组 (原始响应字符串, 总结文本, 任务列表)
        """
        api_base = self.config.get("llm_api_base", "")
        api_key = self.config.get("llm_api_key", "")
        model = self.config.get("llm_model", "")
        
        if not api_key:
            self.logger.error("LLM API Key 未配置")
            raise LLMClientError("LLM API Key 未配置")
        
        try:
            raw_response = call_llm_for_group_chat_summary(
                chat_text=chat_text,
                api_base=api_base,
                api_key=api_key,
                model=model
            )
            
            # 去除 markdown 代码块标记（如果存在）
            import re
            cleaned_response = raw_response
            if "```" in cleaned_response:
                # 匹配 ```json ... ``` 或 ``` ... ``` 格式
                pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
                match = re.search(pattern, cleaned_response, re.DOTALL)
                if match:
                    cleaned_response = match.group(1).strip()
            
            result_data = safe_json_loads(cleaned_response, {})
            summary = result_data.get("summary", "")
            tasks_data = result_data.get("tasks", [])
            
            tasks = []
            for task_item in tasks_data:
                task = Task(
                    task=task_item.get("task", ""),
                    assignee=task_item.get("assignee"),
                    deadline=task_item.get("deadline"),
                    raw_text=task_item.get("raw_text", "")
                )
                tasks.append(task)
            
            return raw_response, summary, tasks
        except LLMClientError as e:
            self.logger.error(f"调用 LLM 失败: {e}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"解析 LLM 响应 JSON 失败: {e}")
            raise
        except Exception as e:
            self.logger.error(f"处理 LLM 响应失败: {e}")
            raise

    def save_results_to_file(self, date: str, group_id: str, raw_response: str, summary: str, tasks: List[Task]) -> str:
        """保存结果到文件（使用防御性工具函数）。

        Args:
            date: 日期字符串，格式 "YYYY-MM-DD"
            group_id: 群组 ID
            raw_response: LLM 原始响应
            summary: 群聊总结
            tasks: 任务列表

        Returns:
            保存的文件路径
        """
        output_dir = self.config.get("summary_output_dir", "summaries")
        
        if not os.path.isabs(output_dir):
            output_dir = os.path.join(str(self.workspace), output_dir)
        
        safe_make_dirs(output_dir)
        
        safe_date = safe_filename(date)
        safe_group_id = safe_filename(group_id)
        filename = f"{safe_date}_{safe_group_id}_{datetime.now().strftime('%H%M%S')}.json"
        safe_filename_str = safe_filename(filename)
        filepath = safe_join_path(output_dir, safe_filename_str)
        
        result_data = {
            "date": date,
            "group_id": group_id,
            "generated_at": datetime.now().isoformat(),
            "summary": summary,
            "raw_response": raw_response,
            "tasks": [task.to_dict() for task in tasks]
        }
        
        json_content = safe_json_dumps(result_data)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(json_content)
        
        self.logger.info(f"结果已保存到: {filepath}")
        return filepath

    async def daily_summary(self):
        """每日总结定时任务回调。"""
        self.logger.info("开始执行每日总结任务...")
        
        try:
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            self.logger.info(f"处理日期: {yesterday}")
            
            if "messages" not in self.data or yesterday not in self.data["messages"]:
                self.logger.info(f"{yesterday} 没有消息数据")
                return
            
            day_messages = self.data["messages"][yesterday]
            monitored_groups = self.config.get("monitored_groups", [])
            
            for group_id, messages in day_messages.items():
                if monitored_groups and group_id not in monitored_groups:
                    continue
                
                self.logger.info(f"处理群组 {group_id} 的消息，共 {len(messages)} 条")
                
                try:
                    if not messages:
                        self.logger.info(f"群组 {group_id} 没有消息")
                        continue
                    
                    formatted_text = self.format_group_messages(messages)
                    self.logger.debug(f"格式化后的消息: {formatted_text[:200]}...")
                    
                    try:
                        raw_response, summary, tasks = await self.call_llm_and_extract_tasks(formatted_text)
                        self.logger.info(f"群组 {group_id} 成功生成总结，提取到 {len(tasks)} 个任务")
                    except Exception as e:
                        self.logger.error(f"群组 {group_id} 调用 LLM 失败: {e}", exc_info=True)
                        continue
                    
                    try:
                        file_path = self.save_results_to_file(yesterday, group_id, raw_response, summary, tasks)
                        self.logger.info(f"群组 {group_id} 结果已保存到 {file_path}")
                    except Exception as e:
                        self.logger.error(f"群组 {group_id} 保存结果失败: {e}", exc_info=True)
                        continue
                    
                    # 发送总结（支持图片）
                    await self._send_summary_to_groups(
                        group_id=group_id,
                        summary=summary,
                        tasks=tasks,
                        raw_response=raw_response,
                        message_count=len(messages),
                        is_dynamic=False,
                        messages=messages
                    )
                
                except Exception as e:
                    self.logger.error(f"处理群组 {group_id} 时发生错误: {e}", exc_info=True)
                    continue
            
            self.logger.info("每日总结任务执行完成")
        
        except Exception as e:
            self.logger.error(f"每日总结任务执行失败: {e}", exc_info=True)
    
    async def _dynamic_summary_loop(self):
        """后台协程：定期检查各群空闲时间，空闲超过设定值则触发总结。"""
        idle_seconds = self.config.get("dynamic_summary_idle_minutes", 10) * 60
        min_messages = self.config.get("dynamic_summary_min_messages", 5)
        
        self.logger.info(f"⚡ 动态总结后台任务启动，检查间隔: {idle_seconds}秒")
        
        while True:
            try:
                await asyncio.sleep(30)  # 每30秒检查一次
                
                if not self.config.get("dynamic_summary_enabled", False):
                    continue
                
                current_time = asyncio.get_event_loop().time()
                today = datetime.now().strftime("%Y-%m-%d")
                
                if "messages" not in self.data or today not in self.data["messages"]:
                    continue
                
                for group_id, last_time in list(self._last_message_time.items()):
                    elapsed = current_time - last_time
                    
                    if elapsed >= idle_seconds:
                        messages = self.data["messages"][today].get(group_id, [])
                        
                        # 检查消息数量是否达到阈值
                        if len(messages) >= min_messages:
                            self.logger.info(f"⚡ 群 {group_id} 空闲 {elapsed:.0f} 秒，触发动态总结（消息数: {len(messages)}）")
                            
                            async with self._summary_lock:
                                await self._send_dynamic_summary(group_id, today, messages)
                            
                            # 清空该群今日消息（已总结）
                            self.data["messages"][today][group_id] = []
                        
                        # 重置计时（无论是否触发总结）
                        self._last_message_time[group_id] = current_time
                        
            except asyncio.CancelledError:
                self.logger.info("⚡ 动态总结任务已取消")
                break
            except Exception as e:
                self.logger.error(f"⚡ 动态总结循环异常: {e}", exc_info=True)
                await asyncio.sleep(60)
    
    async def _send_summary_to_groups(
        self,
        group_id: str,
        summary: str,
        tasks: List[Task],
        raw_response: str,
        message_count: int = 0,
        is_dynamic: bool = True,
        messages: List[Dict[str, Any]] = None
    ):
        """发送总结到指定群（支持文本和图片模式）。"""
        if not self.config.get("send_to_group", False):
            return
        
        try:
            summary_target_groups = self.config.get("summary_target_groups", [])
            target_groups = summary_target_groups if summary_target_groups else [group_id]
            
            summary_as_image = self.config.get("summary_as_image", True) and HAS_PLAYWRIGHT
            
            if summary_as_image:
                # 生成图片
                theme = self.config.get("summary_image_theme", "colorful")
                title = "会话总结" if is_dynamic else "每日总结"
                time_str = datetime.now().strftime("%H:%M") if is_dynamic else ""
                
                image_path = await generate_summary_image(
                    title=title,
                    summary=summary,
                    tasks=tasks,
                    group_id=group_id,
                    output_path=None,
                    theme=theme,
                    messages=messages,
                    show_timeline=True
                )
                
                if image_path and os.path.exists(image_path):
                    # 发送图片
                    for target_group in target_groups:
                        try:
                            # 使用 send_group_image 发送图片
                            await self.api.platform("qq").send_group_image(
                                group_id=target_group,
                                image=image_path
                            )
                            self.logger.info(f"{'⚡' if is_dynamic else '📊'} 总结图片已发送到群 {target_group}")
                        except Exception as e:
                            self.logger.error(f"发送图片到群 {target_group} 失败: {e}")
                    
                    # 清理临时文件
                    try:
                        os.remove(image_path)
                    except:
                        pass
                else:
                    self.logger.warning("图片生成失败，回退到文本模式")
                    await self._send_text_summary(target_groups, summary, tasks, is_dynamic)
            else:
                # 文本模式
                await self._send_text_summary(target_groups, summary, tasks, is_dynamic)
                
        except Exception as e:
            self.logger.error(f"发送总结失败: {e}", exc_info=True)
    
    async def _send_text_summary(
        self,
        target_groups: List[str],
        summary: str,
        tasks: List[Task],
        is_dynamic: bool
    ):
        """发送文本格式总结。"""
        task_list_text = "\n".join([
            f"• {task.task}" + (f" (负责人: {task.assignee})" if task.assignee else "") + (f" (截止: {task.deadline})" if task.deadline else "")
            for task in tasks
        ]) if tasks else "暂无任务"
        
        time_str = datetime.now().strftime("%H:%M")
        prefix = "⚡" if is_dynamic else "📊"
        summary_msg = f"{prefix} [{time_str}] {'会话' if is_dynamic else '每日'}总结\n\n{summary}\n\n📋 任务:\n{task_list_text}"
        
        for target_group in target_groups:
            try:
                await self.api.platform("qq").post_group_msg(group_id=target_group, text=summary_msg)
                self.logger.info(f"{prefix} 文本总结已发送到群 {target_group}")
            except Exception as e:
                self.logger.error(f"发送文本到群 {target_group} 失败: {e}")

    async def _trigger_instant_summary(self, group_id: str, triggered_by: str, triggered_by_name: str):
        """触发即时总结（由 !总结 命令触发）。"""
        # 防止重复触发
        if not hasattr(self, '_instant_summary_locks'):
            self._instant_summary_locks = {}
        
        lock = self._instant_summary_locks.get(group_id)
        if lock is None:
            lock = asyncio.Lock()
            self._instant_summary_locks[group_id] = lock
        
        if lock.locked():
            self.logger.info(f"⏳ 群 {group_id} 已有即时总结正在进行，跳过重复触发")
            return
        
        async with lock:
            try:
                self.logger.info(f"🎯 触发即时总结，群: {group_id}，触发者: {triggered_by_name} ({triggered_by})")
                
                # 检查是否有消息数据
                if "messages" not in self.data or today not in self.data["messages"]:
                    await self._send_command_reply(group_id, "📭 今天还没有收集到消息呢~")
                    return
                
                messages = self.data["messages"][today].get(group_id, [])
                
                if not messages:
                    await self._send_command_reply(group_id, "📭 当前群今天还没有消息记录~")
                    return
                
                # 发送处理中提示
                await self._send_command_reply(group_id, f"🤖 {triggered_by_name} 触发了即时总结，正在生成中...")
                
                # 生成总结
                formatted_text = self.format_group_messages(messages)
                
                try:
                    raw_response, summary, tasks = await self.call_llm_and_extract_tasks(formatted_text)
                    self.logger.info(f"📢 群 {group_id} 即时总结生成成功，任务数: {len(tasks)}")
                except Exception as e:
                    self.logger.error(f"📢 群 {group_id} 即时总结 LLM 调用失败: {e}")
                    await self._send_command_reply(group_id, f"❌ 总结生成失败: {str(e)[:50]}")
                    return
                
                # 保存结果
                try:
                    self.save_results_to_file(today, group_id, raw_response, summary, tasks)
                except Exception as e:
                    self.logger.error(f"📢 保存即时总结结果失败: {e}")
                
                # 发送总结（支持图片）
                await self._send_summary_to_groups(
                    group_id=group_id,
                    summary=summary,
                    tasks=tasks,
                    raw_response=raw_response,
                    message_count=len(messages),
                    is_dynamic=True,
                    messages=messages
                )
                
                # 清空该群今日消息（已手动总结，避免重复）
                self.data["messages"][today][group_id] = []
                self.logger.info(f"📢 群 {group_id} 即时总结完成，已清空今日消息缓存")
                
            except Exception as e:
                self.logger.error(f"📢 即时总结处理异常: {e}", exc_info=True)
                try:
                    await self._send_command_reply(group_id, f"❌ 总结处理异常: {str(e)[:50]}")
                except:
                    pass
    
    async def _send_command_reply(self, group_id: str, text: str):
        """发送命令回复消息。"""
        try:
            await self.api.platform("qq").post_group_msg(group_id=group_id, text=text)
        except Exception as e:
            self.logger.error(f"发送命令回复失败: {e}")

    async def _send_dynamic_summary(self, group_id: str, date: str, messages: List[dict]):
        """发送动态总结到指定群。"""
        try:
            if not messages:
                return
            
            formatted_text = self.format_group_messages(messages)
            
            try:
                raw_response, summary, tasks = await self.call_llm_and_extract_tasks(formatted_text)
                self.logger.info(f"⚡ 群 {group_id} 动态总结生成成功，任务数: {len(tasks)}")
            except Exception as e:
                self.logger.error(f"⚡ 群 {group_id} 动态总结 LLM 调用失败: {e}")
                return
            
            # 保存结果
            try:
                self.save_results_to_file(date, group_id, raw_response, summary, tasks)
            except Exception as e:
                self.logger.error(f"⚡ 保存动态总结结果失败: {e}")
            
            # 发送到群（支持图片）
            await self._send_summary_to_groups(
                group_id=group_id,
                summary=summary,
                tasks=tasks,
                raw_response=raw_response,
                message_count=len(messages),
                is_dynamic=True,
                messages=messages
            )
                    
        except Exception as e:
            self.logger.error(f"⚡ 动态总结处理异常: {e}", exc_info=True)

    async def on_close(self):
        if hasattr(self, '_msg_listener_task') and self._msg_listener_task:
            self._msg_listener_task.cancel()
            try:
                await self._msg_listener_task
            except asyncio.CancelledError:
                pass
        if hasattr(self, '_private_listener_task') and self._private_listener_task:
            self._private_listener_task.cancel()
            try:
                await self._private_listener_task
            except asyncio.CancelledError:
                pass
        if hasattr(self, '_dynamic_summary_task') and self._dynamic_summary_task:
            self._dynamic_summary_task.cancel()
            try:
                await self._dynamic_summary_task
            except asyncio.CancelledError:
                pass
        if hasattr(self, '_avatar_reply_task') and self._avatar_reply_task:
            self._avatar_reply_task.cancel()
            try:
                await self._avatar_reply_task
            except asyncio.CancelledError:
                pass
        self.logger.info(f"{self.name} 已卸载")

    async def _avatar_reply_queue_loop(self):
        """私聊回复队列处理循环（按顺序一个一个回复）。"""
        self.logger.info("🎭 私聊回复队列处理循环已启动")
        while True:
            try:
                # 从队列取出一个消息
                item = await self._avatar_reply_queue.get()
                sender_id = item['sender_id']
                sender_name = item['sender_name']
                content = item['content']
                
                self.logger.info(f"🎭 队列处理消息 - {sender_name} ({sender_id}), 队列长度: {self._avatar_reply_queue.qsize()}")
                
                # 处理回复
                await self._process_avatar_reply(sender_id, sender_name, content)
                
                # 标记完成
                self._avatar_reply_queue.task_done()
                
                # 稍作停顿避免消息过快
                await asyncio.sleep(0.5)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"🎭 队列处理异常: {e}")
                await asyncio.sleep(1)
    
    async def _process_avatar_reply(self, sender_id: str, sender_name: str, content: str):
        """实际处理分身回复逻辑。"""
        try:
            # 检查冷却期：用户最近是否手动回复过（防止队列中已入队消息在冷却期内仍被回复）
            if self._is_avatar_cooling_down(sender_id):
                self.logger.info(f"🎭 队列中消息来自 {sender_name} ({sender_id})，但处于冷却期，跳过回复")
                return  # 跳过这个回复
            
            # 获取分身提示词（基础 + 学习后的增强）
            base_prompt = self.config.get("avatar_prompt", "")
            if not base_prompt:
                return
            
            # 生成学习后的增强提示词（如果有足够的样本）
            avatar_prompt = await self._generate_learned_prompt(base_prompt, sender_id)
            
            # 构建对话上下文（最多20条，超长自动压缩）
            today = datetime.now().strftime("%Y-%m-%d")
            private_key = f"private_{sender_id}"
            all_messages = []
            
            if "messages" in self.data and today in self.data["messages"]:
                if private_key in self.data["messages"][today]:
                    all_messages = self.data["messages"][today][private_key]
            
            # 构建上下文 - 明确区分双方身份
            MAX_CONTEXT = 20
            bot_uin = str(self.config.get("bot_uin", "0"))
            my_name = "NeuTronM"
            
            conversation_history = ""
            
            # 提取历史对话，明确标记"我"和"对方"
            def format_message(msg):
                msg_sender_id = str(msg.get("sender_id", ""))
                msg_sender_name = msg.get("sender_name", "未知")
                msg_text = msg.get("content", "")
                if msg_sender_id == bot_uin:
                    return f"我({my_name}): {msg_text}"
                else:
                    return f"对方({msg_sender_name}): {msg_text}"
            
            if len(all_messages) > MAX_CONTEXT:
                # 压缩早期对话
                old_messages = all_messages[:-(MAX_CONTEXT-5)]
                recent_messages = all_messages[-(MAX_CONTEXT-5):]
                
                old_history = ""
                for msg in old_messages:
                    old_history += format_message(msg) + "\n"
                
                compressed_summary = await self._compress_conversation(old_history, avatar_prompt)
                if compressed_summary:
                    conversation_history = f"[早期对话摘要] {compressed_summary}\n\n"
                
                for msg in recent_messages[:-1]:  # 排除当前消息
                    conversation_history += format_message(msg) + "\n"
            else:
                for msg in all_messages[:-1]:  # 排除当前消息
                    conversation_history += format_message(msg) + "\n"
            
            # 添加当前消息（标记为对方）
            conversation_history += f"对方({sender_name}): {content}\n"
            
            # 构建 LLM 提示词 - 强调身份
            system_prompt = f"""{avatar_prompt}

重要：你的名字叫"NeuTronM"（钟梓珉），是第一人称"我"。对方是正在和你对话的人。请根据以下对话历史，以"我"的身份回复"对方"的消息。注意区分"我"说过的话和"对方"说过的话，只回复"对方"的最新消息。"""
            user_prompt = f"对话历史:\n{conversation_history}\n\n现在请回复对方({sender_name})的这条消息: {content}"
            
            # 调用 LLM
            api_base = self.config.get("llm_api_base", "")
            api_key = self.config.get("llm_api_key", "")
            model = self.config.get("llm_model", "")
            
            client_kwargs = {
                "api_key": api_key,
                "timeout": 15
            }
            if api_base:
                client_kwargs["base_url"] = api_base
            
            client = openai.OpenAI(**client_kwargs)
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            if response.choices and response.choices[0].message.content:
                reply_text = response.choices[0].message.content.strip()
                
                # 发送回复
                await self.api.platform("qq").post_private_msg(
                    user_id=sender_id,
                    text=reply_text
                )
                
                self.logger.info(f"🎭 已回复 {sender_name}: {reply_text[:50]}...")
                
                # 记录自己的回复到消息历史
                self.data["messages"][today][private_key].append({
                    "sender_id": str(self.config.get("bot_uin", "0")),
                    "sender_name": "NeuTronM",
                    "content": reply_text,
                    "timestamp": int(datetime.now().timestamp()),
                    "source": "private"
                })
            
        except Exception as e:
            self.logger.error(f"🎭 处理回复失败: {e}")

import os
import json
import asyncio
import html
import datetime
from pathlib import Path
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.helpers import mention_html

# ---------- 配置 ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID", "0"))
VERIFY_QUESTION = os.getenv("VERIFY_QUESTION", "请输入访问密码：")
VERIFY_ANSWER = os.getenv("VERIFY_ANSWER", "123456")

PERSIST_FILE = Path("/data/topic_mapping.json")

if not BOT_TOKEN: raise RuntimeError("❌ 请设置 BOT_TOKEN")
if GROUP_ID == 0: raise RuntimeError("❌ 请设置 GROUP_ID")

# ---------- 内存数据 ----------
user_to_thread = {}
thread_to_user = {}
user_verified = {}
banned_users = set()

def get_now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 加载数据
if PERSIST_FILE.exists():
    try:
        content = PERSIST_FILE.read_text(encoding="utf-8")
        if content.strip():
            data = json.loads(content)
            user_to_thread = {int(k): int(v) for k, v in data.get("user_to_thread", {}).items()}
            thread_to_user = {int(k): int(v) for k, v in data.get("thread_to_user", {}).items()}
            user_verified = {int(k): v for k, v in data.get("user_verified", {}).items()}
            banned_users = set(data.get("banned_users", []))
            print(f"[{get_now()}] DEBUG: 成功加载 {len(user_to_thread)} 条记录。")
    except Exception as e:
        print(f"[{get_now()}] DEBUG: 加载失败: {e}")

def persist_mapping():
    """持久化保存"""
    data = {
        "user_to_thread": {str(k): v for k, v in user_to_thread.items()},
        "thread_to_user": {str(k): v for k, v in thread_to_user.items()},
        "user_verified": {str(k): v for k, v in user_verified.items()},
        "banned_users": list(banned_users),
    }
    try:
        if not PERSIST_FILE.parent.exists(): PERSIST_FILE.parent.mkdir(parents=True, exist_ok=True)
        PERSIST_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"[{get_now()}] ERROR: 写入失败: {e}")

# ---------- 核心检测与创建逻辑 ----------
async def _ensure_thread_for_user(context: ContextTypes.DEFAULT_TYPE, user_id: int, display: str):
    """确保话题存在，并实时验证其有效性"""
    topic_name = f"ID_{user_id}_{display}"[:30]
    
    # 1. 如果内存里有记录，先验证它是否真的还在
    if user_id in user_to_thread:
        tid = user_to_thread[user_id]
        try:
            # 关键动作：尝试修改话题名称作为“探测”
            # 如果话题被删了，这一步会立刻抛出异常
            await context.bot.edit_forum_topic(chat_id=GROUP_ID, message_thread_id=tid, name=topic_name)
            return tid, False # 验证通过，直接返回
        except Exception as e:
            err = str(e).lower()
            if any(x in err for x in ["not found", "invalid", "closed"]):
                print(f"[{get_now()}] DEBUG: 检测到话题 {tid} 已失效，准备清理并重建...")
                user_to_thread.pop(user_id)
                thread_to_user.pop(tid, None)
                persist_mapping()
                # 继续向下执行创建逻辑
            else:
                # 如果是权限等其他错误，暂且认为还在
                return tid, False

    # 2. 创建新话题
    print(f"[{get_now()}] DEBUG: 正在为用户 {user_id} 创建新话题...")
    resp = await context.bot.create_forum_topic(chat_id=GROUP_ID, name=topic_name)
    new_tid = int(resp.message_thread_id)
    
    user_to_thread[user_id] = new_tid
    thread_to_user[new_tid] = user_id
    persist_mapping()
    return new_tid, True

async def _send_card(context, uid, user, thread_id):
    """发送新用户名片"""
    safe_name = html.escape(user.full_name or "未知")
    username = f"@{user.username}" if user.username else "未设置"
    text = f"<b>新用户接入</b>\nID: <code>{uid}</code>\n名字: {mention_html(uid, safe_name)}\n用户名: {username}\n#id{uid}"
    try:
        await context.bot.send_message(chat_id=GROUP_ID, message_thread_id=thread_id, text=text, parse_mode=ParseMode.HTML)
    except: pass

# ---------- 处理器 ----------
async def handle_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_chat.type != "private": return
    uid = update.effective_user.id
    user = update.effective_user
    msg = update.message

    if uid in banned_users: return

    # 1. 验证逻辑
    if not user_verified.get(uid):
        content = msg.text or msg.caption or ""
        if content.strip() == VERIFY_ANSWER:
            user_verified[uid] = True
            persist_mapping()
            await msg.reply_text("验证成功！")
        else:
            await msg.reply_text(VERIFY_QUESTION)
        return

    display = (user.full_name or user.username or str(uid)).replace("\n", " ")
    
    # 2. 获取并验证话题（如果被删了，这里会自动完成重建）
    thread_id, is_new = await _ensure_thread_for_user(context, uid, display)
    
    if is_new:
        await _send_card(context, uid, user, thread_id)

    # 3. 转发消息
    try:
        print(f"[{get_now()}] DEBUG: 正在转发消息到话题 {thread_id}")
        await context.bot.copy_message(chat_id=GROUP_ID, message_thread_id=thread_id, from_chat_id=uid, message_id=msg.message_id)
        await msg.reply_text("已送达。")
    except Exception as e:
        print(f"[{get_now()}] ERROR: 转发失败: {e}")
        await msg.reply_text(f"发送失败，请稍后再试。")

async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """群内回话转发回私聊"""
    msg = update.message
    if not msg or update.effective_chat.id != GROUP_ID: return
    if msg.is_topic_message and msg.forum_topic_created: return
    
    thread_id = getattr(msg, "message_thread_id", None)
    if not thread_id: return 

    target_uid = thread_to_user.get(int(thread_id))
    if target_uid:
        try:
            await context.bot.copy_message(chat_id=target_uid, from_chat_id=GROUP_ID, message_id=msg.message_id)
        except Exception as e:
            print(f"[{get_now()}] ERROR: 回复用户失败: {e}")

# ---------- 其它命令 ----------
async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"用户ID: <code>{update.effective_user.id}</code>\n群组ID: <code>{update.effective_chat.id}</code>", parse_mode=ParseMode.HTML)

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != GROUP_ID or not context.args: return
    try:
        uid = int(context.args[0])
        if uid in user_to_thread:
            tid = user_to_thread.pop(uid)
            thread_to_user.pop(tid, None)
            persist_mapping()
            await update.message.reply_text(f"✅ 已重置用户 {uid}。")
    except: pass

def main():
    print(f"[{get_now()}] Bot is starting...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # 重新注册所有命令
    app.add_handler(CommandHandler("start", handle_private_message))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("reset", reset_command))
    
    app.add_handler(MessageHandler(filters.Chat(chat_id=GROUP_ID) & ~filters.COMMAND & ~filters.StatusUpdate.ALL, handle_group_message))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & ~filters.COMMAND, handle_private_message))
    
    app.run_polling()

if __name__ == "__main__":
    main()

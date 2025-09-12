#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 功能：私聊发给机器人视频/图片/文字，会发布到对应频道
#       支持超链接（裸 URL 或 文字(链接)）
#       额外功能：/del <id> 删除频道消息
#               /edit <id> <新内容> 修改频道消息或说明文字
#               /pin <id>   置顶当前id信息

import re
from telegram import Update, Bot, ParseMode
from telegram.ext import Updater, MessageHandler, CallbackContext, CommandHandler, Filters

# 机器人 Token
TOKEN = '7673625328:AAGdiTpUH_AbNEYIuYa1LvbdUw-9AbE2r3A'  # @admittyybot

# 创建机器人
bot = Bot(token=TOKEN)

# 目标频道
target_channel_username = '@yunvgongshaonvge'
target_channel_id = bot.get_chat(target_channel_username).id


def clean_caption(caption: str) -> str:
    """清理文字内容，去掉广告行但保留链接"""
    if not caption:
        return ""
    lines = []
    for line in caption.splitlines():
        if re.search(r'(当前第|频道)', line):
            continue
        if re.fullmatch(r'\s*@\w+\s*', line):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def convert_bracket_links(text: str) -> str:
    """
    把 '文字(https://example.com)' 转成 HTML 超链接
    """
    if not text:
        return text
    pattern = re.compile(r'([^\(\)]+)\((https?://[^\s\)]+)\)')
    return pattern.sub(r'<a href="\2">\1</a>', text)


def looks_like_html_anchor(text: str) -> bool:
    """检查文本是否包含 HTML <a> 标签"""
    if not text:
        return False
    return bool(re.search(r'<a\s+href\s*=', text, flags=re.IGNORECASE))


def forward_to_channel(update: Update, context: CallbackContext):
    """转发私聊消息到频道"""
    try:
        message = update.message
        if not message:
            return

        # 视频
        if message.video:
            cleaned_caption = clean_caption(message.caption)
            cleaned_caption = convert_bracket_links(cleaned_caption)
            parse_mode = ParseMode.HTML if looks_like_html_anchor(cleaned_caption) else None
            sent = context.bot.send_video(
                chat_id=target_channel_id,
                video=message.video.file_id,
                caption=cleaned_caption if cleaned_caption else None,
                parse_mode=parse_mode
            )
            message.reply_text(f"✅ 视频已发布到频道\n🆔 消息ID: {sent.message_id}")
            return

        # 图片
        if message.photo:
            clearest_photo = max(message.photo, key=lambda p: p.width * p.height)
            cleaned_caption = clean_caption(message.caption)
            cleaned_caption = convert_bracket_links(cleaned_caption)
            parse_mode = ParseMode.HTML if looks_like_html_anchor(cleaned_caption) else None
            sent = context.bot.send_photo(
                chat_id=target_channel_id,
                photo=clearest_photo.file_id,
                caption=cleaned_caption if cleaned_caption else None,
                parse_mode=parse_mode
            )
            message.reply_text(f"✅ 图片已发布到频道\n🆔 消息ID: {sent.message_id}")
            return

        # 文本
        if message.text:
            cleaned_text = clean_caption(message.text)
            cleaned_text = convert_bracket_links(cleaned_text)
            if not cleaned_text:
                message.reply_text("⚠️ 内容为空，未发布。")
                return
            parse_mode = ParseMode.HTML if looks_like_html_anchor(cleaned_text) else None
            sent = context.bot.send_message(
                chat_id=target_channel_id,
                text=cleaned_text,
                parse_mode=parse_mode,
                disable_web_page_preview=False
            )
            message.reply_text(f"✅ 文本已发布到频道\n🆔 消息ID: {sent.message_id}")
            return

    except Exception as e:
        print(f"❌ 转发出错: {e}")
        try:
            update.message.reply_text(f"⚠️ 出错: {e}")
        except:
            pass


def delete_message(update: Update, context: CallbackContext):
    """删除频道消息"""
    try:
        if not context.args:
            update.message.reply_text("⚠️ 用法: /del <消息ID>")
            return
        msg_id = int(context.args[0])
        context.bot.delete_message(chat_id=target_channel_id, message_id=msg_id)
        update.message.reply_text(f"✅ 已删除频道中 ID {msg_id} 的消息")
    except Exception as e:
        update.message.reply_text(f"⚠️ 删除失败: {e}")


def edit_message(update: Update, context: CallbackContext):
    """修改频道消息"""
    try:
        if len(context.args) < 2:
            update.message.reply_text("⚠️ 用法: /edit <消息ID> <新内容>")
            return
        msg_id = int(context.args[0])
        new_text = " ".join(context.args[1:])
        new_text = convert_bracket_links(new_text)
        parse_mode = ParseMode.HTML if looks_like_html_anchor(new_text) else None

        # 先尝试修改文本消息
        try:
            context.bot.edit_message_text(
                chat_id=target_channel_id,
                message_id=msg_id,
                text=new_text,
                parse_mode=parse_mode
            )
            update.message.reply_text(f"✅ 已修改文本消息 ID {msg_id}")
        except:
            # 如果是媒体消息，只能改 caption
            context.bot.edit_message_caption(
                chat_id=target_channel_id,
                message_id=msg_id,
                caption=new_text,
                parse_mode=parse_mode
            )
            update.message.reply_text(f"✅ 已修改媒体消息说明 ID {msg_id}")

    except Exception as e:
        update.message.reply_text(f"⚠️ 修改失败: {e}")

def pin_message(update: Update, context: CallbackContext):
    """置顶频道消息"""
    try:
        if not context.args:
            update.message.reply_text("⚠️ 用法: /pin <消息ID>")
            return
        msg_id = int(context.args[0])
        context.bot.pin_chat_message(chat_id=target_channel_id, message_id=msg_id, disable_notification=True)
        update.message.reply_text(f"📌 已将频道消息 ID {msg_id} 置顶")
    except Exception as e:
        update.message.reply_text(f"⚠️ 置顶失败: {e}")


# 添加消息处理器
updater = Updater(token=TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(MessageHandler(Filters.all & ~Filters.command, forward_to_channel))
dp.add_handler(CommandHandler("del", delete_message))
dp.add_handler(CommandHandler("edit", edit_message))
dp.add_handler(CommandHandler("pin", pin_message))


# 启动机器人
print("🤖 机器人已启动：私聊发内容 → 发布到频道；/del 删除；/edit 修改（支持超链接）")
updater.start_polling()
updater.idle()

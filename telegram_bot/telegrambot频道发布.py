#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 功能：私聊发给机器人视频，会发布到对应的频道里
# 新增功能：/del <消息id> 删除频道中的指定帖子

import re
from telegram import Update, Bot
from telegram.ext import Updater, MessageHandler, CallbackContext, Filters, CommandHandler

# 机器人 Token
TOKEN = '7673625328:AAGdiTpUH_AbNEYIuYa1LvbdUw-9AbE2r3A'  # @admittyybot

# 创建机器人
bot = Bot(token=TOKEN)

# 目标频道用户名（可以写 @频道名 或 -100xxxxxxxxxxx）
target_channel_username = '@yunvgongshaonvge'
target_channel_id = bot.get_chat(target_channel_username).id


def clean_caption(caption: str) -> str:
    """清理文字内容，去掉广告/链接"""
    if not caption:
        return ""

    cleaned = "\n".join(
        line for line in caption.splitlines()
        if not re.search(r'(当前第|频道|http[s]?://|@\w+)', line)
    )

    cleaned = re.sub(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F]{2}))+',
        '',
        cleaned
    )
    return cleaned.strip()


def forward_to_channel(update: Update, context: CallbackContext):
    """转发消息到频道"""
    try:
        message = update.message
        if not message:
            return

        if message.video:  # 视频
            cleaned_caption = clean_caption(message.caption)
            sent = context.bot.send_video(
                chat_id=target_channel_id,
                video=message.video.file_id,
                caption=cleaned_caption
            )
            message.reply_text(f"✅ 视频已发布到频道\n������ 消息ID: {sent.message_id}")

        elif message.photo:  # 图片（选最大分辨率）
            clearest_photo = max(message.photo, key=lambda p: p.width * p.height)
            cleaned_caption = clean_caption(message.caption)
            sent = context.bot.send_photo(
                chat_id=target_channel_id,
                photo=clearest_photo.file_id,
                caption=cleaned_caption
            )
            message.reply_text(f"✅ 图片已发布到频道\n������ 消息ID: {sent.message_id}")

        elif message.text:  # 文本
            cleaned_text = clean_caption(message.text)
            if cleaned_text:
                sent = context.bot.send_message(chat_id=target_channel_id, text=cleaned_text)
                message.reply_text(f"✅ 文本已发布到频道\n������ 消息ID: {sent.message_id}")

    except Exception as e:
        print(f"❌ 出错: {e}")
        update.message.reply_text(f"⚠️ 出错: {e}")


def delete_message(update: Update, context: CallbackContext):
    """删除频道中的指定消息"""
    try:
        if len(context.args) != 1:
            update.message.reply_text("⚠️ 用法：/del 消息ID")
            return

        msg_id = int(context.args[0])
        context.bot.delete_message(chat_id=target_channel_id, message_id=msg_id)
        update.message.reply_text(f"✅ 已删除频道中 ID {msg_id} 的消息")

    except Exception as e:
        print(f"❌ 删除出错: {e}")
        update.message.reply_text(f"⚠️ 删除出错: {e}")


# 添加消息处理器
updater = Updater(token=TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(MessageHandler(Filters.all & ~Filters.command, forward_to_channel))
dp.add_handler(CommandHandler("del", delete_message))

# 启动机器人
print("������ 机器人已启动，可以私聊它发送图片/视频/文本，会自动转发到频道，也支持 /del 删除频道消息")
updater.start_polling()
updater.idle()

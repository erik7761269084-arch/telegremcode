#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telethon import TelegramClient
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights

# ========= 配置区域 =========
api_id = 123456          # 在 my.telegram.org 申请
api_hash = "your_api_hash"
phone = "+8613812345678" # 你的主号（必须是频道的拥有者或管理员）
channel_username = "@yunvgongshaonvge"  # 频道用户名
user_to_promote = "admittyybot"         # 想设置为管理员的账号，可以填 @用户名 或 user_id

# ========= 权限设置 =========
rights = ChatAdminRights(
    change_info=True,      # 修改群/频道信息
    post_messages=True,    # 发消息
    edit_messages=True,    # 编辑别人的消息
    delete_messages=True,  # 删除消息
    ban_users=True,        # 封禁用户
    invite_users=True,     # 邀请用户
    pin_messages=True,     # 置顶消息
    add_admins=True,       # 添加新的管理员
    manage_call=True,      # 管理语音聊天
    anonymous=False,       # 是否匿名管理员
)

# ========= 主逻辑 =========
async def main():
    async with TelegramClient("session_admin", api_id, api_hash) as client:
        # 获取频道
        channel = await client.get_entity(channel_username)
        # 获取目标用户
        user = await client.get_entity(user_to_promote)

        # 设置管理员
        await client(EditAdminRequest(
            channel=channel,
            user_id=user,
            admin_rights=rights,
            rank="管理员"  # 管理员头衔
        ))

        print(f"✅ 已成功把 {user_to_promote} 设置为 {channel_username} 的管理员")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

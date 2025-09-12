#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import requests
from bs4 import BeautifulSoup
import time
import re

# ==== 数据库配置 ====
db_host = "192.168.1.9"
db_user = "root"
db_pass = "123456"
db_name = "telegramsousuo"
db_table = "telegramhtml"

# ==== 请求头，伪装浏览器 ====
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/139.0.0.0 Safari/537.36"
}

# ==== 连接数据库 ====
conn = pymysql.connect(
    host=db_host,
    user=db_user,
    password=db_pass,
    database=db_name,
    charset="utf8mb4"
)
cursor = conn.cursor()

# ==== 获取所有频道链接 ====
cursor.execute(f"SELECT id, telegramhtml FROM {db_table}")
rows = cursor.fetchall()

# ==== 更新数据库语句 ====
update_sql = f"""
UPDATE {db_table}
SET channel_name=%s, member_count=%s, status=%s
WHERE id=%s
"""

updated_count = 0

for rec_id, channel_link in rows:
    try:
        # 请求频道网页
        resp = requests.get(channel_link, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            print(f"⚠️ 无法访问 {channel_link}，状态码 {resp.status_code}")
            status = "已失效"
            channel_name = ""
            member_count = 0
        else:
            soup = BeautifulSoup(resp.text, "html.parser")

            # 获取频道名称
            title_tag = soup.find("div", class_="tgme_page_title")
            channel_name = title_tag.get_text(strip=True) if title_tag else "未知"

            # 获取成员数
            members_tag = soup.find("div", class_="tgme_page_extra")
            member_count = 0
            if members_tag:
                text = members_tag.get_text(strip=True)
                match = re.search(r'(\d+)', text)
                if match:
                    member_count = int(match.group(1))

            status = "已失效" if channel_name == "未知" or member_count == 0 else "正常"

        # 更新数据库
        cursor.execute(update_sql, (channel_name, member_count, status, rec_id))
        conn.commit()
        updated_count += 1
        print(f"✅ 更新 {channel_link} -> 名称: {channel_name}, 人数: {member_count}, 状态: {status}")

        # 避免请求过快被封
        time.sleep(1)

    except Exception as e:
        print(f"❌ 处理 {channel_link} 出错: {e}")
        continue

cursor.close()
conn.close()
print(f"✅ 数据库更新完成，共更新 {updated_count} 条记录")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import requests
from bs4 import BeautifulSoup
import re
import time

# ==== 数据库配置 ====
db_host = "192.168.1.9"
db_user = "root"
db_pass = "123456"
db_name = "telegramsousuo"
db_table = "telegramhtml"

# ==== 指定起始ID ====
start_id = 10612  # 从这个ID开始处理，可修改

# ==== 连接数据库 ====
conn = pymysql.connect(
    host=db_host,
    user=db_user,
    password=db_pass,
    database=db_name,
    charset="utf8mb4"
)
cursor = conn.cursor()

# ==== 获取指定起始ID之后的所有链接，按 id 升序 ====
cursor.execute(f"SELECT id, telegramhtml FROM {db_table} WHERE id >= %s ORDER BY id ASC", (start_id,))
rows = cursor.fetchall()

# ==== 请求头 ====
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/117.0.0.0 Safari/537.36"
}

# ==== 更新 SQL ====
update_sql = f"""
UPDATE {db_table}
SET channel_name=%s, member_count=%s, status=%s
WHERE id=%s
"""

updated_count = 0

for rec_id, link in rows:
    # 默认值
    channel_name = "未知"
    member_count = 0
    status = "未知"

    try:
        resp = requests.get(link, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")

            # 获取频道名称
            title_tag = soup.find("div", class_="tgme_page_title")
            if title_tag:
                channel_name = title_tag.get_text(strip=True)

            # 获取成员数
            members_tag = soup.find("div", class_="tgme_page_extra")
            if members_tag:
                text = members_tag.get_text(strip=True)
                # 匹配数字和空格，例如 "104 311"
                match = re.search(r'([\d\s]+)', text)
                if match:
                    # 去掉空格再转整数
                    member_count = int(match.group(1).replace(" ", ""))

            # 状态判断
            status = "已失效" if channel_name == "未知" or member_count == 0 else "正常"

        else:
            status = "已失效"

    except Exception as e:
        print(f"❌ 处理 {link} 出错: {e}")
        status = "已失效"

    # 更新数据库
    cursor.execute(update_sql, (channel_name, member_count, status, rec_id))
    conn.commit()
    updated_count += 1
    print(f"✅ id: {rec_id},{link} -> 名称: {channel_name}, 人数: {member_count}, 状态: {status}")

    time.sleep(1)  # 防止请求过快

# ==== 关闭数据库 ====
cursor.close()
conn.close()
print(f"✅ 已更新 {updated_count} 条记录")

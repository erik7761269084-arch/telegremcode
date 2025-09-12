#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
from urllib.parse import urlparse

# ==== 数据库配置 ====
db_host = "192.168.1.9"
db_user = "root"
db_pass = "123456"
db_name = "telegramsousuo"
db_table = "telegramhtml"

# ==== 文件路径 ====
file_path = r"E:\telegremcode\电报数据采集\only_links.txt"

# ==== 从第几行开始（1 表示第一行，2 表示从第二行开始，以此类推）====
start_line = 1   # 👉 修改这里即可，比如 100 表示从第100行开始

# ==== 读取文件并去重 ====
with open(file_path, "r", encoding="utf-8") as f:
    all_lines = [line.strip() for line in f if line.strip()]

# 只取从指定行开始的部分
all_lines = all_lines[start_line - 1:]  # 下标从 0 开始，所以减 1

# 使用 set 去重
links = set(all_lines)

# ==== 连接数据库 ====
conn = pymysql.connect(
    host=db_host,
    user=db_user,
    password=db_pass,
    database=db_name,
    charset="utf8mb4"
)
cursor = conn.cursor()

# ==== 创建表（如果不存在） ====
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {db_table} (
    id INT AUTO_INCREMENT PRIMARY KEY,
    telegramhtml VARCHAR(255) NOT NULL UNIQUE COMMENT '频道链接',
    channel_name VARCHAR(255) DEFAULT NULL COMMENT '频道名称',
    status ENUM('正常','已失效') DEFAULT '正常' COMMENT '频道状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""
cursor.execute(create_table_sql)

# ==== 插入数据，保证唯一性 ====
insert_sql = f"""
INSERT IGNORE INTO {db_table} (telegramhtml, channel_name)
VALUES (%s, %s)
"""
inserted_count = 0
for link in links:
    # 只保留频道/群主页链接，不要子路径
    if link.startswith("https://t.me/"):
        parsed = urlparse(link)
        path = parsed.path.lstrip('/')
        if path and '/' not in path:  # 去掉子路径
            channel_name = path
            cursor.execute(insert_sql, (link, channel_name))
            inserted_count += 1

# ==== 提交事务并关闭 ====
conn.commit()
cursor.close()
conn.close()

print(f"✅ 已成功写入 {inserted_count} 条数据到 {db_table} 表（重复自动忽略）")
print(f"📌 本次处理从第 {start_line} 行开始，总计 {len(all_lines)} 行")

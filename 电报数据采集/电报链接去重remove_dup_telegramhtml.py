#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from bs4 import BeautifulSoup

# ==== 配置 ====
html_dir = r"C:\Users\Admin\Downloads\Telegram Desktop\ChatExport_2025-09-12"
output_file = os.path.join(html_dir, "output_links.txt")

# ==== 扫描目录 ====
all_links = set()  # 用 set 自动去重

for root, dirs, files in os.walk(html_dir):
    for file in files:
        if file.lower().endswith(".html") or file.lower().endswith(".htm"):
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()
                soup = BeautifulSoup(html_content, "html.parser")
                for a_tag in soup.find_all("a", href=True):
                    href = a_tag['href'].strip()
                    if href.startswith("https://t.me/"):
                        # 去掉消息ID或子路径，只保留频道主页
                        parts = href.split('/')
                        if len(parts) >= 4:
                            channel_link = f"{parts[0]}//{parts[2]}/{parts[3]}"
                        else:
                            channel_link = href
                        all_links.add(channel_link)

# ==== 写入到文本文件 ====
with open(output_file, "w", encoding="utf-8") as f:
    for link in sorted(all_links):
        f.write(link + "\n")

print(f"✅ 已完成提取 {len(all_links)} 条去重后的 Telegram 频道链接，保存到 {output_file}")

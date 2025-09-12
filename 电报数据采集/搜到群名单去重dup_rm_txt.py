#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

# 输入文件路径
input_file = r"E:\telegremcode\电报数据采集\搜索群名单.txt"
# 输出文件路径
output_file = r"E:\telegremcode\电报数据采集\搜索群名单_去重.txt"

# 是否按 a-z 排序（True = 排序，False = 保留原始顺序）
sort_enabled = True

# 读取文件并去重（保留原始大小写）
seen = set()
unique_links = []
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        link = line.strip()
        if link and link.lower() not in seen:  # 忽略大小写去重
            seen.add(link.lower())
            unique_links.append(link)

# 可选排序
if sort_enabled:
    unique_links = sorted(unique_links, key=lambda x: x.lower())

# 写回去重后的结果
with open(output_file, "w", encoding="utf-8") as f:
    for link in unique_links:
        f.write(link + "\n")

print(f"✅ 去重完成，结果已保存到 {output_file}，共 {len(unique_links)} 条")
if sort_enabled:
    print("🔠 已按 A-Z 排序")
else:
    print("📌 保留原始顺序")

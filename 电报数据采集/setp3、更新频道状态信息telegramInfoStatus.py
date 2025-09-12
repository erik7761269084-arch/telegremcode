#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import requests
from bs4 import BeautifulSoup
import re
import time

# ==== ���ݿ����� ====
db_host = "192.168.1.9"
db_user = "root"
db_pass = "123456"
db_name = "telegramsousuo"
db_table = "telegramhtml"

# ==== �������ݿ� ====
conn = pymysql.connect(
    host=db_host,
    user=db_user,
    password=db_pass,
    database=db_name,
    charset="utf8mb4"
)
cursor = conn.cursor()

# ==== ��ȡ�������ӣ��� id ���� ====
cursor.execute(f"SELECT id, telegramhtml FROM {db_table} ORDER BY id ASC")
rows = cursor.fetchall()

# ==== ����ͷ ====
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/139.0.0.0 Safari/537.36"
}

# ==== ���� SQL ====
update_sql = f"""
UPDATE {db_table}
SET channel_name=%s, member_count=%s, status=%s
WHERE id=%s
"""

updated_count = 0

for rec_id, link in rows:
    # Ĭ��ֵ
    channel_name = "δ֪"
    member_count = 0
    status = "δ֪"

    try:
        resp = requests.get(link, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")

            # ��ȡƵ������
            title_tag = soup.find("div", class_="tgme_page_title")
            if title_tag:
                channel_name = title_tag.get_text(strip=True)

            # ��ȡ��Ա��
            members_tag = soup.find("div", class_="tgme_page_extra")
            if members_tag:
                text = members_tag.get_text(strip=True)
                match = re.search(r'(\d+)', text)
                if match:
                    member_count = int(match.group(1))

            # ״̬�ж�
            status = "��ʧЧ" if channel_name == "δ֪" or member_count == 0 else "����"

        else:
            status = "��ʧЧ"

    except Exception as e:
        print(f"? ���� {link} ����: {e}")
        status = "��ʧЧ"

    # �������ݿ�
    cursor.execute(update_sql, (channel_name, member_count, status, rec_id))
    conn.commit()
    updated_count += 1
    print(f"? {link} -> ����: {channel_name}, ����: {member_count}, ״̬: {status}")

    time.sleep(1)  # ��ֹ�������

# ==== �ر����ݿ� ====
cursor.close()
conn.close()
print(f"? �Ѹ��� {updated_count} ����¼")

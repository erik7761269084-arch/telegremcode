import os
import re
import hashlib

# 设置要检查的目录
folder = r"E:\test小说"  # 修改为你的视频目录

def file_hash(filepath):
    """计算文件内容的 MD5 哈希"""
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def extract_number(filename):
    """提取文件名里的 (数字)，没有则返回 0"""
    match = re.search(r"\((\d+)\)", filename)
    return int(match.group(1)) if match else 0

def remove_duplicate_mp4(folder):
    seen = {}
    deleted = 0

    for filename in os.listdir(folder):
        # 只处理 .mp4 文件
        if not filename.lower().endswith(".mp4"):
            continue

        filepath = os.path.join(folder, filename)
        file_md5 = file_hash(filepath)

        if file_md5 not in seen:
            seen[file_md5] = [filepath]
        else:
            seen[file_md5].append(filepath)

    # 遍历每组重复的 mp4 文件
    for files in seen.values():
        if len(files) > 1:
            # 优先保留：无编号 > 编号小的
            files.sort(key=lambda f: (extract_number(f), len(os.path.basename(f))))
            keep = files[0]  # 保留第一个
            print(f"保留: {keep}")
            for f in files[1:]:
                print(f"删除重复视频: {f}")
                os.remove(f)
                deleted += 1

    print(f"✅ 去重完成，共删除 {deleted} 个重复 mp4 文件")

if __name__ == "__main__":
    remove_duplicate_mp4(folder)

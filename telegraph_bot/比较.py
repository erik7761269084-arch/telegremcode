import requests
from bs4 import BeautifulSoup
from telegraph import Telegraph
from datetime import datetime
import re
import os
import sys
from telegraph.exceptions import TelegraphException


switch_del_content_words = True   #删除内容文字，只保留图片

# 要复制的 telegraph 页面列表
SOURCE_URLS = []
TXT_FILE = r"D:\project\pythonLL\telegraph_links_福利姬.txt"
# 优先从 txt 文件读取
if TXT_FILE and os.path.exists(TXT_FILE):
    with open(TXT_FILE, "r", encoding="utf-8") as f:
        SOURCE_URLS = [line.strip() for line in f if line.strip()]
else:
    # 如果没有 txt，就用内置的列表
    SOURCE_URLS = [ ]

# SOURCE_URLS = [
# "https://telegra.ph/BRbINz-09-05",
# "https://telegra.ph/mymUJf-08-28",
#
# ]

# 新的作者信息
AUTHOR_NAME = "御女宫福利姬频道←点击关注"
AUTHOR_URL = "https://erik7761269084-arch.github.io/-/%E7%A6%8F%E5%88%A9%E5%A7%AC%E9%A2%91%E9%81%93%E6%80%BB%E7%9B%AE%E5%BD%95/index.html"

# AUTHOR_NAME = "御女宫漫画频道←点击关注"
# AUTHOR_URL = "https://erik7761269084-arch.github.io/-/%E6%BC%AB%E7%94%BB%E9%A2%91%E9%81%93%E6%80%BB%E7%9B%AE%E5%BD%95/index.html"

# AUTHOR_NAME = "御女宫小说频道←点击关注"
# AUTHOR_URL = "https://erik7761269084-arch.github.io/-/%E5%B0%8F%E8%AF%B4%E9%A2%91%E9%81%93%E6%80%BB%E7%9B%AE%E5%BD%95/index.html"


ALLOWED_TAGS = {
    "p", "br", "strong", "b", "i", "em", "u", "a",
    "blockquote", "img", "video", "h3", "h4",
    "pre", "code", "ul", "ol", "li", "figure", "figcaption"
}

def clean_content(article):
    """清理正文，不保留原作者和副标题"""
    # 删除原作者段落
    for p in article.find_all("p"):
        if any(keyword in p.get_text() for keyword in ["关注频道", "cosplay写真频道"]):
            p.decompose()

    # 删除 header、h1/h2、address 等
    for tag in article.find_all(["header", "h1", "h2", "address"]):
        tag.decompose()

    # 清理不支持标签
    for tag in article.find_all(True):
        if tag.name not in ALLOWED_TAGS:
            tag.unwrap()

    if switch_del_content_words:

        NEWALLOWED_TAGS = ["figure", "img"]

        # 遍历所有标签
        for tag in article.find_all(True):
            if tag.name not in NEWALLOWED_TAGS:
                tag.decompose()  # 删除标签及内容

        # # 删除 <strong>、<blockquote> 里的内容
        # for tag in article.find_all(["strong", "blockquote"]):
        #     tag.decompose()

    return "".join(str(child) for child in article.contents)

def extract_title(header_tag):
    """从 header 中提取干净的标题，只保留核心文字"""
    if not header_tag:
        return "无标题"
    text = header_tag.get_text(strip=True)

    # 去掉广告/副标题/日期等
    text = re.split(r"cosplay写真频道|每日百合本推送|风月文学|←点击关注|百万图集免费看|👉🏻.*", text)[0].strip()

    # 再次截断，防止漏掉广告词
    text = re.split(r"(cosplay|频道|每日百合本推送|风月文学|Isabelle|http|←点击关注|百万图集免费看|👉🏻.*)", text, 1)[0].strip()

    # 定义要删除的广告关键词（直接切掉，不影响后面内容）
    remove_keywords = [
        "[中国翻訳]",
        "[提黄灯喵汉化组×碧蓝档案百合组×一青二白汉化组]",
        "[Chinese]",
        "[网红COSER写真]",
        "[网红COS]",
        "[网红COSER]",
        "[Cosplay写真]",
        "[COS福利]",
        "[梦丝女神MSLASS]",
        "[Digi-Gra]",
        "[LOVEPOP]",
        "[BLUECAKE]",
        "[Cosplay]",
        "[秀人XiuRen]",
        "[福利COS]",
        "[喵糖映画]",
        "[萝莉COS]",
        "[尤蜜YouMi]",
        "[尤蜜YouMiabc]",
        "[爱尤物Ugirls]",
        "[秀人XIUREN]",
        "[兔玩映画]",
        "[风之领域]",
        "[模范学院MFStar]",
        "[[糖果画报CANDY]]",
        "[嗲囡囡FEILIN]",
        "[秀人网XiuRen]",
        "[美媛馆MyGirl]",
        "[尤物馆YouWu]",
        "[Bololi波萝社]",
        "[MF萌缚]",
        "[御女郎DKGirl]",
        "[Fantasy Factory]",
        "[SSA丝社]",
        "[蜜丝MISSLEG]",
        "[Ligui丽柜]",
        "[秀人XiuRen]",
        "[语画界XIAOYU]",
        "[秀人Xiuren]",
        "[蜜桃社MiiTao]",
        "[爱蜜社IMiss]",
        "[花漾HuaYang]",
        "[尤蜜荟YouMi]",
        "[無修正]",
        "[暴碧汉化组]",
        "[5DK个人汉化]",
        "[中国語]",
        "[猫萌榜MICAT]",
        "[尤果Ugirls]",
        "[FEILIN嗲囡囡]",
        "[TASTE顽味生活]",
        "[尤果圈爱尤物]",
        "[Fantia]",
        "[Xiuren]",
        "fantia",
        "[]",
        "超清",
        "COS少女",
        "可爱人气Coser",
        "人气Coser",
        "微博COS妹子",
        "COS福利",
        "COS妹子",
        "Coser小姐姐",
        "二次元妹子",
        "微博人气Coser",
        "爱丽丝写真",
        "清纯妹子",
        "清纯少女",
        "打包合集",
        "性感动漫Coser@",
        "萌宠博主",
        "微博萌妹",
        "美女主播"
        "电喵女神",
        "喵糖映画-",
        "@"
        "马里奥小屋",
        "动漫博主",
        "可爱妹子",
        "斗鱼主播",
        "二次元巨乳美女",
        "二次元巨乳",
        "阳光美少女",
        "萌系小姐姐",
        "写真",
        "图集",
        "《Fantasy Factory》",
        "Cosplay",
        "二次元少女",
        "次元少女",
        "御女宫漫画(彩色)",
        "御女宫漫画(黑白)",
        "MyGirl美媛馆",
        "人气Coser",
        "动漫博主"
    ]

    for kw in remove_keywords:
        text = text.replace(kw, "")

    # 去掉多余空格
    return text.strip()

    return text


# 登录 telegraph
telegraph = Telegraph()
telegraph.create_account(short_name="copybot")

# 输出 HTML 文件
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
result_html = f"result_{timestamp}.html"

with open(result_html, "w", encoding="utf-8") as f_html:
    for url in SOURCE_URLS:
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, "html.parser")
            # soup.contents[2].contents[1].contents[3].contents[0]
            # 获取干净标题
            header_tag = soup.find("header")
            if (
                    header_tag and
                    len(header_tag.contents) > 1 and
                    header_tag.contents[1].contents
            ):
                # 有内容就取它
                title = header_tag.contents[1].contents[0]
                title = extract_title(title)
            else:
                # 否则调用函数
                title = extract_title(header_tag)

            # 清理正文
            article = soup.find("article")
            content_html = clean_content(article)

            try:
                # 创建新页面
                response = telegraph.create_page(
                    title=title,
                    html_content=content_html,
                    author_name=AUTHOR_NAME,
                    author_url=AUTHOR_URL
                )
            except Exception as e:
                err_msg = str(e)
                if re.search(r"Flood control exceeded", err_msg):
                    print(f"❌ Flood 控制触发，停止程序: {url}")
                    sys.exit(1)  # 直接终止整个脚本
                else:
                    print(f"❌ 处理 {url} 出错: {e}")

            new_url = f"https://telegra.ph/{response['path']}"
            print(f"✅ {title} -> {new_url}")

            # 写入 HTML 文件
            f_html.write(f'<p><a href="{new_url}">{title}</a></p>\n')

        except Exception as e:
            print(f"❌ 处理 {url} 出错: {e}")
            f_html.write(f"<p>❌ 处理 {url} 出错: {e}</p>\n")

print(f"✅ 已生成 HTML 文件: {result_html}")

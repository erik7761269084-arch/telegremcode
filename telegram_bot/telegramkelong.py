# 防止重复资源转发版本
import asyncio
import telethon.errors
import re
import io
import os  # 确保导入 os 模块
import json
from PIL import Image
from telethon import TelegramClient, events, types
from telethon.tl.types import  PeerUser, PeerChannel, PeerChat
from telethon.errors import ChatForwardsRestrictedError, FloodWaitError, WorkerBusyTooLongRetryError
from bs4 import BeautifulSoup # 使用 BeautifulSoup 解析 HTML

# 账号秘钥
config_key = {
    "4367844176129": {
        "api_id": 21188192,
        "api_hash": "e6f77c825e2c10fffdf6a15ffd319193",
        "phone_number": "+4367844176129"  # 使用你的手机号码
    },
    # 20250908号被封
    # "447761269084": {
    #     "api_id": 28044957,
    #     "api_hash": "0ba92315766a94f4b2b1837d5c6df66e",
    #     "phone_number": "+447761269084"   # 使用你的手机号码
    # },
    "447729261613": {
        "api_id": 25464924,
        "api_hash": "227feadd3bf378bf09ed18a57299bea3",
        "phone_number": "+447729261613"   # 使用你的手机号码
    },
    # #目前账号已被封，等待解冻 2025年9月2日封号
    # "447761231417": {
    #     "api_id": 25864626,
    #     "api_hash": "28a00ddf6f55ce4660c415276f6bdc66",
    #     "phone_number": "+447761231417"  # 使用你的手机号码
    # },
    "8618033186883": {
        "api_id": 23263821,
        "api_hash": "424970113de1f7f2d9e20e96d4ea3676",
        "phone_number": "+8618033186883"   # 使用你的手机号码
    },
    # #目前账号已被封，等待解冻
    # "8618033328771": {
    #     "api_id": 24275359,
    #     "api_hash": "f377bb5d9ae2077fc29899fc38c65891",
    #     "phone_number": "+8618033328771"   # 使用你的手机号码
    # },
    "8618033328773": {
        "api_id": 20522852,
        "api_hash": "89e64e1f091781c60d98d61fae422334",
        "phone_number": "+8618033328773"   # 使用你的手机号码
    },
    "8613727515839": {
        "api_id": 23237710,
        "api_hash": "fa956f727c8f5ce367004e4f06980d27",
        "phone_number": "+8613727515839"   # 使用你的手机号码
    }
}

config = {

    # 是否只保存收集 Telegraph 链接
    "switch_download_telegraph": False,

    # 发布超链接到频道
    "html_sender": {
        "switch_send_html": False,
        "send_html_file": r"E:\links.html",
        "telegraph_extra_tag": "#Bambi #밤비"
    },
    # 标题处理
    "caption": {
        "switch_caption": False,         # 是否对标题进行处理开关.以下开关此开关必须为 True
        "switch_del_number": False,      # 添加  #序号
        "NUMBER_CAP": 1,                 #序号 123... 已屏蔽
        "switch_add_title": False,       # 当标题为空时，添加文件名为标题开关
        "switch_add_label": False        # 对文字前面加上# 标签
    },
    # 自定义标签开关
    "Label": {
        "switch_string": False,
        "global_string": "\n#旧录屏 (2022年之前作品)"
    },
    # 关键词筛选
    "Keywords": {
        "switch_words": False,
        "target_words": ["香港"]
    },
    # 下载视频图片配置
    "download_media": {
        "switch_download_media": False,     # 下载频道资源
        "download_dir": "下载文件名称"        # 下载文件名称
    },

}

def select_account(key):
    account = config_key.get(key)
    if not account:
        raise ValueError(f"Key {key} 不存在！")
    return account["api_id"], account["api_hash"], account["phone_number"]

# 使用示例：
chosen_key = "447729261613"      # 你想选哪个 key
api_id, api_hash, phone = select_account(chosen_key)

# 源频道和目标频道的ID
# Peertype = 'me'              # 获取 "我的收藏" 用户本身收藏夹
# Peertype = 'robot'             # 对象是机器人的类型的话
# Peertype = 'PeerUser'          # 个人聊天类型
Peertype = 'PeerChannel'        #频道类型

target_channels = {
    "source_channel_id": 1572778714,
    "target_channel_id": 2993909759,
    "Y1国内柚": 2287884497,
    "Y2欧美柚": 2265724101,
    "Y3幼童": 2265724101,
    "Y4插入小白菜": 2457042432,
    "Y5网调小白菜": 2372594560,
    "Y6小马拉大车": 1761473246,
    "S1小白菜散装": 2554661715,
    "S2少女约炮":   2497436586,
    "S3越南少女":   2678257385,
    "S4缅甸少女":   2420122522,
    "S5欧美少女":   2677564610,
    "S6韩国少女":   2261927152,
    "S7日本少女":   1908896631,
    "S8少女霸凌":   2327145247,
    "S9破处少女":   1504995259,
    "C1国内痴汉":   2625494809,
    "C2欧美痴汉":   2398853954,
    "C3日本痴汉":   2180977000,
    "C4母乳":      2596584959,
    "C5街拍频道":   2515576216,
    "C6人与动物":   2574683434,
    "C8迷奸频道":   2673399332,
    "C9厕拍":      2668260550,
    "C10漫展频道":  2578545687,
    "C11后宫欧美":  2605533299,
    "C11后宫国内":  2541756787,
    "C12砂舞":     2616708464,
    "C13KTV":     2454839038,
    "C14闪现走光": 2558006962,
    "T9媚黑婊":    2423252523,
    "T11女同":     2590957161,
    "K2撩B社":     2618347510,
    "VIP国内柚Y1": 2903114589,
    "VIP母乳C4":   2915798581,
    "健身女孩资源来源": 3026352613,
    "水果派AV解说福利社": 2090605054,   #14078-14112
    "砂舞C12": 2616708464,
    "VIP砂舞": 2730009473,
    "收集水果派": 2983201884,
    "收集健身女孩": 3007997929,
    "收集三级片未整理去重": 2862613270,
    "收集三级片": 2862613270,
    "收集国产AV": 2900356030,
    "御女宫国产av1": 3067771961,
    "御女宫三级片": 2909770699,
    "御女宫健身女孩": 2932386237,
    "御女宫小说频道": 2993909759,
    "御女宫福利姬频道": 2761208549,
    "御女宫漫画频道": 2934360954,
    "御女宫少女阁": 2971937398,
    "御女宫水果派": 3045559209,
    "御女宫音乐": 2935049435,
    "御女宫泳装": 2850188495
}

source_channel_id = target_channels["Y1国内柚"]
target_channel_id = target_channels["VIP国内柚Y1"]

# 指定从哪个 ID 开始和结束
global_start_id = 1
global_end_id = 19645
global_end_id += 1  # 最后一个加一，不然会漏掉最后一个

global_send_count = 1   #转发数量最大值数组;

# 记录最终转发的 ID 号
final_forwarded_id = None

# 定义等待时间（秒）
wait_time_seconds = 200

# 用于存储所有相册组的二维列表
all_album_group = [[]]
current_media_group = []
current_media_group_title = None
# 创建Telegram客户端实例
client = None

# 标题最大长度
MAX_CAPTION_LENGTH = 1024
MAX_LENGTH = 1024

# 创建客户端开发账号更换开关
switch_account = False  # True

# 文件路径，用于记录已转发的消息ID
directory = r"D:\project\python\unique_filename"  # 文件存放路径

# HTML 文件路径
switch_send_html = config["html_sender"]["switch_send_html"]

# 定义全局变量
switch_caption = config["caption"]["switch_caption"]           # 是否对标题进行处理开关
switch_del_number = config["caption"]["switch_del_number"]     # 去除开头的纯数字（可带空格）
NUMBER_CAP = config["caption"]["NUMBER_CAP"]                   # 序号标签
switch_add_label = config["caption"]["switch_add_label"]       # 对文字前面加上# 标签
switch_add_title = config["caption"]["switch_add_title"]       # 当标题为空时，添加文件名为标题开关
switch_string = config["Label"]["switch_string"]  # 自定义标签开关
global_string = config["Label"]["global_string"]
switch_number = False    # 初始化 NUMBER_COUNT，从 1 开始
NUMBER_COUNT = 1        #从1开始标签号
switch_TT_link = False
global_TT_link = '\n[极搜导航](http://t.me/ttshaonvchat)\n[soso导航](http://t.me/ttsososo)\n[搜一搜导航](http://t.me/ttsouyisou)\n[TT总部](http://t.me/ttzongb)'

# 使用 os.path.join 拼接路径
forwarded_ids_file = os.path.join(directory, str(target_channel_id) + ".txt")  # 文件名称的绝对地址
forwarded_hash_ids_file = os.path.join(directory, str(target_channel_id) + "_hash.txt")  # 文件名称的绝对地址

switch_send_html = config["html_sender"]["switch_send_html"]
switch_download_media = config["download_media"]["switch_download_media"]   # 开启下载，而不是转发数据
switch_download_telegraph = config["switch_download_telegraph"]             # 是否保存 Telegraph 链接
switch_save_video_ID = False  # 检测视频重复数据
switch_save_hash_ID = True  # 检测文件重复数据
switch_words = config["Keywords"]["switch_words"]  # 筛选关键词开关，是否匹配转发
flag_add_album = False
switch_message_text = False  # 转发文字消息开关

message_document_video_ids = set()
message_document_hash_ids = set()

# 创建文件路径
dict_file = os.path.join(directory, str(target_channel_id) + "_dict.txt")  # 留言字典集合
title_dict_file = os.path.join(directory, str(target_channel_id) + "title_dict.txt")  # 标题字典集合

# 创建一个空字典
my_dict = {}  # 留言字典
my_title_dict = {}  # 标题字典

# 读取已转发的消息ID
def load_forwarded_hash_ids():
    if os.path.exists(forwarded_hash_ids_file):
        with open(forwarded_hash_ids_file, "r") as f:
            return set(int(line.strip()) for line in f.readlines())
    return set()


# 保存已转发的消息ID
def save_forwarded_hash_ids(ids):
    existing_ids = set()
    # 如果文件存在，读取现有内容以检查唯一性
    if os.path.exists(forwarded_hash_ids_file):
        with open(forwarded_hash_ids_file, "r") as f:
            for line in f:
                existing_ids.add(line.strip())

    new_ids = [id for id in ids if str(id) not in existing_ids]
    # 以追加模式打开文件并写入新的唯一 ID
    with open(forwarded_hash_ids_file, "a") as f:
        for doc_id in new_ids:
            f.write(f"{doc_id}\n")


# 读取已转发的消息ID
def load_forwarded_ids():
    if os.path.exists(forwarded_ids_file):
        with open(forwarded_ids_file, "r") as f:
            return set(int(line.strip()) for line in f.readlines())
    return set()


# 保存已转发的消息ID
def save_forwarded_ids(ids):
    existing_ids = set()
    # 如果文件存在，读取现有内容以检查唯一性
    if os.path.exists(forwarded_ids_file):
        with open(forwarded_ids_file, "r") as f:
            for line in f:
                existing_ids.add(line.strip())

    new_ids = [id for id in ids if str(id) not in existing_ids]
    # 以追加模式打开文件并写入新的唯一 ID
    with open(forwarded_ids_file, "a") as f:
        for doc_id in new_ids:
            f.write(f"{doc_id}\n")


async def send_message_with_delay(client, target, message):
    while True:
        try:
            await client.send_message(target, message)
            break  # 成功发送后退出循环
        except FloodWaitError as e:
            print(f"FloodWaitError: Waiting for {e.seconds} seconds.")
            await asyncio.sleep(e.seconds)  # 等待指定的时间


# 选择性筛选关键词函数
def check_sensitive_words(message_content):
    if message_content is None:
        return False
    target_words = config["Keywords"]["target_words"]
    contains_target_word = any(word in message_content for word in target_words)
    return contains_target_word

#将当前列表添加到列表集合 all_album_group 中去
async def add_current_group_to_allalbumgroup(source_channel_id, target_entity, message):
    """处理媒体组的转发逻辑"""
    global all_album_group, current_media_group, current_media_group_title

    # 检查 current_media_group 是否为空
    if not current_media_group:  # 或者使用 if len(current_media_group) == 0:
        return  # 直接返回

    print(f"source_channel_id = {source_channel_id} Forwarding media group as album...")

    # 清空标题
    current_media_group_title = None

    # 将当前媒体组添加到所有相册组
    all_album_group[-1].extend(current_media_group)
    all_album_group.append([])

    # 如果all_album_group的长度超过global_send_count且第一个组不为空，则发送消息组
    # if len(all_album_group) >= global_send_count and len(all_album_group[0]) != 0:
    if len(all_album_group) >= global_send_count and (len(all_album_group) != 1 or len(all_album_group[0]) != 0):
        await check_and_send_media_group(target_entity)

    # 清空当前消息组列表，并将当前消息添加到新的消息组列表中
    current_media_group.clear()
    current_media_group.append(message)  # 将当前消息作为新的消息组
    current_media_group_title = message.text  # 更新标题

async def main():
    global final_forwarded_id, all_album_group, current_media_group, current_media_group_title, client, forwarded_ids, forwarded_ids_photo, global_string, global_TT_link, message_document_video_ids, message_document_hash_ids, my_dict, my_title_dict, dict_file, title_dict_file, global_start_id, global_send_count, flag_add_album  # 声明使用全局变量
    # 读取已转发的消息ID
    forwarded_ids = load_forwarded_ids()
    forwarded_ids_photo = load_forwarded_hash_ids()

    if switch_account:
        # 关闭之前的客户端连接
        if client:
            await client.disconnect()

        # 创建Telegram客户端实例，并指定新的会话名称
        client = TelegramClient('new_session_name', api_id, api_hash)

    async with client:
        # for source_channel_id in source_channel_ids:
            if Peertype == 'PeerUser':
                source_entity = await client.get_entity(PeerUser(source_channel_id))  # 个人聊天 ID
            elif Peertype == 'PeerChannel':
                source_entity = await client.get_entity(PeerChannel(source_channel_id))  # 频道或群组 ID
            elif Peertype == 'robot':
                source_entity = await client.get_entity(source_channel_id) #机器人用id
                # source_entity = await client.get_input_entity(source_channel_id)
                # source_entity = await client.resolve_peer(source_channel_id)
            elif Peertype == 'me':
                source_entity = await client.get_entity('me')  # 获取 "我的收藏" 对话
            else:
                raise ValueError(f"未识别的 Peertype: {Peertype}")
            target_entity = await client.get_entity(PeerChannel(target_channel_id))
            # 获取源频道的最新消息，假设你只需要最新的一条消息
            latest_message = await client.get_messages(source_entity, limit=1)
            end_id = latest_message[0].id + 1

            if source_channel_id == 7487513532:
                start_id = 300695
                end_id = 316249
            else:
                start_id = global_start_id
                end_id = global_end_id

            print(f"Source ID {source_channel_id} Entity:", source_entity)
            print(f"Target ID {target_channel_id} Entity:", target_entity)

            # 检测视频重复数据ID，是否开启
            if switch_save_video_ID:
                # 尝试加载字典
                if os.path.exists(dict_file) and os.path.getsize(dict_file) > 0:
                    with open(dict_file, 'r', encoding='utf-8') as f:
                        my_dict = json.load(f)
                else:
                    my_dict = {}  # 初始化为空字典

            # 尝试加载字典
            if os.path.exists(title_dict_file) and os.path.getsize(title_dict_file) > 0:
                with open(title_dict_file, 'r', encoding='utf-8') as f:
                    my_title_dict = json.load(f)
            else:
                my_title_dict = {}  # 初始化为空字典

            # 用于存储当前消息组的消息列表
            current_media_group = []
            current_media_group_title = None

            # 发布超链接到频道
            if switch_send_html:
                # 读取文件内容（HTML 格式）
                with open(config["html_sender"]["send_html_file"], "r", encoding="utf-8") as f:
                    html_content = f.read()

                soup = BeautifulSoup(html_content, "html.parser")

                for a_tag in soup.find_all("a"):
                    url = a_tag.get("href")
                    text = a_tag.get_text(strip=True)
                    if url and text:
                        message = f'<a href="{url}">{text}</a>\n{config["html_sender"]["telegraph_extra_tag"]}'
                        await client.send_message(target_entity, message, parse_mode='html')
                        print(f"发布超链接 {text}")
                print(f"超链接发布完毕")
                return

            # 获取源频道的所有消息并转发到目标频道（从头到尾）
            for batch_start in range(start_id, end_id + 1, 100):
                messages = await client.get_messages(source_entity,
                                                     ids=list(range(batch_start, min(end_id, batch_start + 100))))
                for message in messages:
                    if message is None:
                        # 处理 message 为 None 的情况
                        print(f"{source_channel_id} Message is None. Continuing...")
                        continue

                    if switch_download_telegraph:

                        if message.entities:
                            try:
                                newurl = None

                                # 1. 优先从 entities 中提取链接
                                for ent in message.entities:
                                    if hasattr(ent, "url") and ent.url:
                                        if re.match(r"^https?://telegra\.ph/", ent.url):
                                            newurl = ent.url
                                            break

                                # 2. 如果 entities 没有，尝试从 cached_page 里找
                                if not newurl and hasattr(message, "media") and message.media:
                                    if hasattr(message.media, "webpage") and message.media.webpage:
                                        if hasattr(message.media.webpage,
                                                   "cached_page") and message.media.webpage.cached_page:
                                            if hasattr(message.media.webpage.cached_page, "url"):
                                                url = message.media.webpage.cached_page.url
                                                if url and re.match(r"^https?://telegra\.ph/", url):
                                                    newurl = url

                                # 3. 保存链接
                                if newurl:
                                    await save_telegraph_links(newurl, "telegraph_links_exhentai五星漫画.txt")
                                    print(f"当前id [{message.id}] ")

                            except Exception as e:
                                print(f"[×] 提取 telegraph 链接失败: {e} 当前id [{message.id}] ")
                        continue

                    # 调用函数并根据返回值进行处理
                    if switch_words:
                        is_sensitive = check_sensitive_words(message.message)
                        if is_sensitive:
                            print("消息中包含敏感词汇")
                            flag_add_album = True
                        else:
                            flag_add_album = False
                            if current_media_group and current_media_group[0].grouped_id != None and message.grouped_id == current_media_group[0].grouped_id:
                                print("跟敏感词汇同组")
                                flag_add_album = True
                            else:
                                is_sensitive_two = False
                                if message.document and len(message.document.attributes) > 1:
                                    if hasattr(message.document.attributes, 'file_name'):  # 是否有 file_name 元素
                                        file_name = message.document.attributes[1].file_name.split('。mp4')[0]
                                        file_name = file_name.split('.mp4')[0]
                                        is_sensitive_two = check_sensitive_words(file_name)
                                if is_sensitive_two:
                                    print("文件标题包含敏感词汇")
                                else:

                                    if flag_add_album == True:
                                        flag_add_album = False
                                        await add_current_group_to_allalbumgroup(source_channel_id, target_entity,message)

                                    print("不转发，不包含敏感词汇且不同组")
                                    continue

                    # 检测视频重复数据ID，是否开启
                    if switch_save_video_ID:
                        # 处理视频重复判断,单独判断视频，比较多，比较快
                        if message.document and message.document.id:
                            if message.document and message.document.id in forwarded_ids:  # 在当前所有记录中
                                continue
                            elif message.document and message.document.id in message_document_video_ids:  # 在100个当中有重合
                                continue
                            else:
                                message_document_video_ids.add(message.document.id)  # 将文件唯一hashID添加到集合中
                        else:
                            print(f"message.document.id is None  message.id == {message.id}")

                    # 检测文件重复数据hash ID，是否开启
                    if switch_save_hash_ID:
                        # 所有类型的hash值唯一判断，图片，视频，文件
                        if message.file is not None:
                            # if message.file.mime_type == 'image/jpeg':
                            if message.file.media.access_hash in forwarded_ids_photo:
                                continue
                            elif message.file.media.access_hash in message_document_hash_ids:
                                continue
                            else:
                                message_document_hash_ids.add(message.file.media.access_hash)  # 将文件唯一hashID添加到集合中

                    # 获取留言字典
                    if message.message:  # 检查 message.message 是否不为空 字典数据，主要是回复数据 比如 1-#111
                        if message.id not in my_dict:
                            my_dict[message.id] = message.message
                            # 将更新后的字典保存到文件
                            with open(dict_file, 'w', encoding='utf-8') as f:
                                json.dump(my_dict, f, ensure_ascii=False, indent=4)

                    # 获取标题字典
                    if message.action is not None:
                        if isinstance(message.action, telethon.tl.types.MessageActionPinMessage):
                            # 针对固定消息的处理
                            # 这里没有 title 属性，可能不需要处理
                            pass
                        elif hasattr(message.action, 'title'):
                            # 处理有 title 属性的消息
                            if message.id not in my_title_dict:
                                my_title_dict[message.id] = message.action.title
                                # 将更新后的字典保存到文件
                                with open(title_dict_file, 'w', encoding='utf-8') as f:
                                    json.dump(my_title_dict, f, ensure_ascii=False, indent=4)
                            if message.id not in my_dict:
                                my_dict[message.id] = message.action.title
                                # 将更新后的字典保存到文件
                                with open(dict_file, 'w', encoding='utf-8') as f:
                                    json.dump(my_dict, f, ensure_ascii=False, indent=4)

                    if message.reply_to_msg_id:  # 检查留言回复 message.reply_to_msg_id 是否不为空
                        value = my_title_dict.get(format(message.reply_to_msg_id))

                        if value is None:  # 键不存在
                            if message.message is None:
                                message.message = ""
                            message.message += my_dict.get(message.reply_to_msg_id,
                                                           "\n 默认值 {}".format(message.reply_to_msg_id))
                        else:
                            if '#' not in value:
                                value = f' \n-  #{value}'
                            else:
                                value = f' \n-  {value}'

                            # 确保 message.message 不为空，若为空则初始化为空字符串
                            if message.message is None:
                                message.message = ""

                            # 如果 value 不为空，将其放在 message.message 最前面，，并加换行符
                            if value:
                                message.message = f"{value}\n{message.message}"

                    print(f"source_channel_id = {source_channel_id} Processing message ID: {message.id}")
                    if message.id > end_id:  # 如果消息 ID 大于结束 ID，则结束循环
                        break

                    if message.id >= start_id:  # 仅处理从开始 ID 到结束 ID 范围内的消息

                        # 如果消息类型为 MessageService，则不处理，直接跳过
                        if isinstance(message, types.MessageService):
                            print(f"source_channel_id = {source_channel_id} Skipping MessageService...")
                            continue

                        if len(all_album_group) >= global_send_count and (len(all_album_group) != 1 or len(all_album_group[0]) != 0):
                            await check_and_send_media_group(target_entity)

                        # 将标题写入到第一个视频或图片中
                        if current_media_group_title is None or current_media_group_title == '':
                            current_media_group_title = message.text

                        # 判断消息是否包含媒体组属性，并且是否为同一媒体组
                        if hasattr(message, 'grouped_id') and message.grouped_id is not None:
                            if not current_media_group or current_media_group[0].grouped_id == message.grouped_id:
                                # 将当前消息添加到消息组列表中
                                current_media_group.append(message)

                                if current_media_group[0].text == '': # 检查 text 为空
                                    current_media_group[0].text = current_media_group_title  # 只有在不为空时才赋值
                            else:
                                # await add_current_group_to_allalbumgroup(source_channel_id, target_entity, message)
                                # 当前消息组与之前的消息组不同，将之前的消息组转发为相册
                                print("Forwarding media group as album...")

                                current_media_group_title = None  # 清空标题

                                all_album_group[-1].extend(current_media_group)
                                all_album_group.append([])
                                # 如果all_album_group的长度超过100，则发送消息组
                                # if len(all_album_group) >= global_send_count and len(all_album_group[0]) != 0:
                                if len(all_album_group) >= global_send_count and (len(all_album_group) != 1 or len(all_album_group[0]) != 0):
                                    await check_and_send_media_group(target_entity)

                                # 清空当前消息组列表，并将当前消息添加到新的消息组列表中
                                current_media_group.clear()
                                current_media_group = [message]
                                current_media_group_title = message.text

                        else:
                            # 当前消息不属于任何媒体组，直接转发
                            print(f"source_channel_id = {source_channel_id} Forwarding individual message...")

                            if message.media:
                                if hasattr(message.media, 'video') or hasattr(message.media, 'photo'):
                                    print("Message contains video")
                                    # 在这里执行您想要的操作
                                    print("Forwarding media group as album...")
                                    all_album_group[-1].extend(current_media_group)
                                    all_album_group.append([])
                                    # 如果all_album_group的长度超过100，则发送消息组
                                    # if len(all_album_group) >= 100:
                                    if len(all_album_group) >= global_send_count and (len(all_album_group) != 1 or len(all_album_group[0]) != 0):
                                        await check_and_send_media_group(target_entity)

                                    # 清空当前消息组列表，并将当前消息添加到新的消息组列表中
                                    current_media_group.clear()
                                    current_media_group_title = None
                                    current_media_group = [message]
                                    current_media_group_title = message.text
                            else:
                                if switch_message_text:
                                    # 调用该函数发送文字消息
                                    caption = modify_string(message.raw_text)
                                    if caption is not None and caption != '':
                                        await send_message_with_delay(client, target_entity, caption)
                                    # 测试，将消息加入到 发送数组中去
                                    # all_album_group[-1].extend(current_media_group)
                                    # all_album_group.append([])
                                    # # 如果all_album_group的长度超过100，则发送消息组
                                    # if len(all_album_group) >= 100:
                                    #     await check_and_send_media_group(target_entity)

                            final_forwarded_id = message.id  # 更新最终转发的 ID 号

            # 处理最后一组消息
            if current_media_group:
                print("Forwarding media group as album...")
                all_album_group[-1].extend(current_media_group)
                await check_and_send_media_group(target_entity)


# 检查并发送消息组成相册
async def check_and_send_media_group(target_entity):
    global all_album_group, current_media_group
    for media_group in all_album_group:
        if media_group:
            while True:
                try:
                    await forward_media_group(media_group, media_group[0].text, target_entity)
                    break  # 如果成功转发，跳出循环
                except telethon.errors.rpcerrorlist.ChatForwardsRestrictedError:
                    # 如果是 ChatForwardsRestrictedError，直接跳过
                    print(f"此资源没有转发权限")
                    break
                except (
                        telethon.errors.rpcerrorlist.FloodWaitError,
                        telethon.errors.rpcerrorlist.MediaInvalidError,telethon.errors.rpcerrorlist.ChatForwardsRestrictedError) as e:
                    # 处理 FloodWaitError 或 MediaInvalidError 异常的代码
                    print(f"FloodWaitError occurred. Waiting for {wait_time_seconds} seconds before continuing...")
                    await asyncio.sleep(wait_time_seconds)

    current_media_group = []
    all_album_group = [[]]


# AV频道特殊处理 片名：xx 前面都是粗体
def process_text(cleaned_text):
    lines = cleaned_text.split('\n')
    formatted_lines = []
    for line in lines:
        if '磁力' in line or 'magnet' in line:
            formatted_lines.append(line)
        else:
            line = line.replace('*', '')
            line = line.replace('`', '')
            line = line.replace('：', ':')
            if ':' in line:
                parts = line.split(':')
                formatted_line = f'**{parts[0]}**：{parts[1]}'
                formatted_lines.append(formatted_line)
            else:
                formatted_lines.append(line)
    formatted_text = '\n'.join(formatted_lines)
    return formatted_text


# 越南频道特殊处理
def process_vietnamese_text(text):
    match = re.search(r'Link', text)
    if match:
        text = ''
        print("Contains 'Link'")
    else:
        print("Does not contain 'Link'")

    text = text.replace('@ttzongb', ' ')

    # if len(re.findall(r'[\u4e00-\u9fa5]', text)) > 40:
    #     text = ''

    return text


# 删除多余链接
def remove_ads(text):
    #特殊处理，现将添加的 "" 去除
    to_remove_list = [
        '搜索引擎一 @ttshaonvchat 搜索引擎二 @ttsososo 搜索引擎三 @ttsouyisou TT防失联总频道 @ttzongb',
        '[������欢迎加入足控恋足会员群]',
        '������  # 输入动漫名发送到搜索群������',
        '������  # 万物可搜， #白嫖更多资源������',
        '== == == == == == == == == == == ==',
        '������  # 女神ai去衣， #点击进群意淫������',
        '✨  # 入会福利',
        '������  # 无码肉番➕3D成人➕ #绝版漫图',
        '������������  # 点击下方链接 #自助购买入会������������',
        '������AI去衣换脸软件  # 点击了解������',
        '[������足控视频群更多美脚恋足足交舔脚资源，欢迎加入������������������������]',
        '[  # 全站导航]',
        '[#全站导航]',
        '[ #商务合作]',
        '关注频道不迷路',
        'haijiaoshequ_456',
    ]

    for item in to_remove_list:
        text = text.replace(item, '')

    text = text.strip()
    # AV频道特殊处理 片名：xx 前面都是粗体
    # text = process_text(text)

    # #越南处理
    # text = process_vietnamese_text(text)

    # 如果字符串中存在 "@" 符号
    if "@" in text:
        # 找到 "@" 符号的位置
        at_index = text.find("@")
        # 找到 "@" 后面的空格的位置
        space_index = text.find("\n", at_index)  # 适用于 @后面是 \n 换行的情况
        if space_index == -1:
            space_index = text.find(" ", at_index)

        if space_index != -1:
            # 删除 "@" 后面的空格及其后面的内容
            # 插入自己的@标签
            link = ' '
            # link = ' [TT总部](http://t.me/ttzongb) '
            text = text[:at_index] + link + text[space_index:]
        else:
            # 如果没有找到，则保留 "@"，只保留前面的内容
            # text = text[:at_index]
            # 找到 @ 后的 ** 是否存在
            after_at = text[at_index:]
            if after_at.endswith('**'):
                # 如果以 ** 结尾，就从 @ 前往前挪 2 位
                return text[:max(0, at_index - 2)]
            else:
                return text[:at_index]


    keywords = ['投稿', '点击', '单击', '复制', '口令', '来源', '完整版', '一键脱衣', '一键去衣', '免费脱衣',
                '脱衣小技巧', '脱衣换脸', '展示区', '更多', '广告', '效果展示', '发张图片试试', '换脸', '更多奶子', 
                '可搜', '教程', '发送给我', '中文包', '吃瓜交流圈', '联系', '克隆', '福利索引', '下载', '客服',
                '翻墙', '机器人', '售后', '进群', '一键关注', '官方合作', 'VPN', '专线', '点亮曝光', '频道互通找到', '@']

    #新增添加
    keywords += ['推荐频道', '老司', '百科', '稳定高速', '地区覆盖', '套餐', '防失联', '老司','优先安排', '帮忙', '条结果', '搜索', '赞助', '查看完整', '频道推送', '@', '私密群', '巨能转载王', '默认值', '更多', 'VIP视频', '跳转到帖子详情', '查看作者其他帖子', '传送门', '导航面板', '一键']
    keywords += ['Free', 'APP','Playstore','Viber', 'Free', 'MDL97', '角色上新', 'AI工具箱', 'AI聊小黄文','女友机器人', '小黄文畅聊', '美图画师', 'AIBox', 'NoveIN', 'AI聊天', 'pixiv', '限时', '自助入群', '吃瓜中心', '频道']

    #缅甸语
    keywords += ['သွင်း', 'ပေး', 'ဂိမ်း']

    #特殊图标
    keywords +=['������', '������', '������ ������ ������ ������',  '������������������������������������������', '❤', '������', '������', '������', '������', '������������', '������', '������','⚽', '������', '������‍❤️‍������', '������', '������', '������', '������', '������', '������', '➖', '������', '������', '������']

    #临时
    keywords += ['友情提醒', '= =', '永久ID', '首字母', '曝光投稿看我主页', 'Download', 'DOWNLOAD', 'Full', 'Patreon', 'Link', 'VOL', 'Nhóm tài nguyên ảnh AI chất lượng tốt tại đây', '★', ]
    formatted_lines = []

    for line in text.split('\n'):
        if any(keyword in line for keyword in keywords): #满足 keywords 任意条件，直接全部删除
            line = ''
        else:
            if line:
                if line.strip():
                    formatted_lines.append(line)
    # #单独针对某一个文字删除
    for i in range(len(formatted_lines)):
        # 对每一行使用 replace 方法
        formatted_lines[i] = formatted_lines[i].replace('91小电影', '')
        formatted_lines[i] = formatted_lines[i].replace('TT防失联总频道', '')
        formatted_lines[i] = formatted_lines[i].replace('[香港_三级]', '')
        formatted_lines[i] = formatted_lines[i].replace('[香港三级]', '')
        formatted_lines[i] = formatted_lines[i].replace('[三级片]', '')
        formatted_lines[i] = formatted_lines[i].replace('[三级影视 ]', '')
        formatted_lines[i] = formatted_lines[i].replace('【新片速递】', '')
        formatted_lines[i] = formatted_lines[i].replace('【制片地区】', '')
        formatted_lines[i] = formatted_lines[i].replace('[香港经典三级系列]', '')
        formatted_lines[i] = formatted_lines[i].replace('#香港三级', '')
        formatted_lines[i] = formatted_lines[i].replace('『三级片名』', '')
        formatted_lines[i] = formatted_lines[i].replace('香港', '')
        formatted_lines[i] = formatted_lines[i].replace('#情色', '')
        formatted_lines[i] = formatted_lines[i].replace('#香港', '')
    #     formatted_lines[i] = re.sub(r'(【[^【】]+】)\1+', r'\1', formatted_lines[i]) #去掉重复的【】，例如 '【欲女】【欲女】 #香港三级'

    return '\n'.join(formatted_lines)


# 修改标题内容
def modify_string(text):
    str = text

    delLinkContext = False
    # 删除超链接和内容
    if delLinkContext:
        # 使用正则表达式匹配并删除 [** 到 **] 的内容
        cleaned_text = re.sub(r'\[\*\*.*?\*\*\]', '', str)

        # 使用正则表达式去掉 magnet 链接和 HTTP/HTTPS 链接
        # cleaned_text = re.sub(r'magnet:[^\s]+|https?://[^\s]+|http?://[^\s]+|[^\s]+\.[^\s]+', '', str)
        str = re.sub(r'https?://[^\s\n]+|http?://[^\s]+|[^\s]+\.[^\s\n]+|t\.me/[^\s\n]+', '', cleaned_text)

    else:
        # 移除HTTP和HTTPS链接,不删除文字
        cleaned_text = re.sub(r'\s*\([^\)]*\)', '', str)

        # 使用正则表达式去掉 magnet 链接和 HTTP/HTTPS 链接
        str = re.sub(r'(magnet:[^\s]+|https?://[^\s]+|http?://[^\s]+|\S+\.[a-z]{2,10}(/\S*)?|t\.me/[^\s]+)', '', cleaned_text, flags=re.IGNORECASE)

    # 删除广告多余内容
    str = remove_ads(str)

    return str

def add_hashtags(text):
    def replacer(match):
        phrase = match.group(0)
        # 如果原本就包含 #，不处理
        if '#' in phrase:
            return phrase
        parts = re.split(r'[_\-\—\s]+', phrase)
        new_parts = [f'#{p.strip()}' for p in parts if p.strip()]
        return ' ' + ' '.join(new_parts)

    # 匹配“连续中文+连接符”但不以 # 开头的段落
    pattern = r'(?<![#\w])([\u4e00-\u9fa5_—\-]{2,})'
    return re.sub(pattern, replacer, text)


def add_hash_inside_brackets(text):
    # 匹配中文中括号包裹的词组，例如 【连体黑丝】
    pattern = r'【(?!#)([\u4e00-\u9fa5]+)】'
    return re.sub(pattern, r'【#\1】', text)

def add_hash_before_chinese(text):
    # 只在没有 # 的中文段前添加 #
    def replacer(match):
        prefix = match.group(1)
        chinese_text = match.group(2)
        # 如果 prefix 是 "#"，说明已经有了，不添加
        if prefix.endswith('#'):
            return match.group(0)
        return prefix + '#' + chinese_text

    pattern = r'(^|[\s])([\u4e00-\u9fa5][^#\n]*)'
    return re.sub(pattern, replacer, text)

def fix_pi_spacing(text):
    # 匹配 π 后的数字，然后匹配一个非法字符（_、-、汉字等），替换为一个空格
    if not text:  # None 或 空字符串
        return ""

    #特殊处理，现将添加的 "" 去除
    to_remove_list = [
        '超多小姐姐福利资源  https://t.me/TG9113',
    ]

    for item in to_remove_list:
        text = text.replace(item, '')

    text = text.strip()

    return re.sub(r'(π\d+)[_\-]|(π\d+)(?=[\u4e00-\u9fff])', lambda m: f"{m.group(1) or m.group(2)} ", text)


# 获取caption标题
def process_caption(messages):
    caption = None
    caption = messages[0].text if messages[0].text else None

    # 在 π后数字后面，如果直接跟汉字，就插入一个空格
    caption = fix_pi_spacing(caption)

    if caption is not None:
        # # 给所有前面不是空格的 # 前加空格
        # caption = re.sub(r'(?<!\s)#', r' #', caption)

        if switch_del_number:
            # caption = '#校报'
            # 去除开头的纯数字（可带空格）
            global NUMBER_CAP
            caption = re.sub(r'^\s*\d+\s*', '', caption)
            caption = f'#序号   \n' + caption
            # caption = f'#序号 {NUMBER_CAP}  \n' + caption
            NUMBER_CAP += 1  # 序号

        caption = modify_string(caption)

        if switch_add_label:
            caption = add_hash_before_chinese(caption)  # 在中文面前加 #
            caption = add_hash_inside_brackets(caption) # 匹配中文中括号包裹的词组，例如 【连体黑丝】
            caption = add_hashtags(caption)             # 处理所有包含中文的短语，按分隔符（_ - — 空格）切分加 #



    if switch_add_title:
        if not caption:
            if messages[0].document and len(messages[0].document.attributes) > 1:
                file_name = messages[0].document.attributes[1].file_name.split('。mp4')[0]
                file_name = file_name.split('.mp4')[0]
                for c in file_name:
                    if '\u4e00' <= c <= '\u9fff':
                        caption = file_name
                        break
                    if re.search('[a-zA-z]', file_name):
                        caption = file_name
                        break

    # # 如果字符串长度大于 MAX_LENGTH，截取前 MAX_LENGTH 个字符
    # if caption is not None and len(caption) > MAX_LENGTH:
    #     caption = caption[:MAX_LENGTH]
    return caption


# 转发消息组成相册
async def forward_media_group(messages, title, target):

    if switch_download_media:
        await download_media_group(messages, title, target)
    else:

        # 构建相册消息
        media = []
        for message in reversed(messages):
            if hasattr(message.media, 'photo') or hasattr(message.media, 'video'):
                media.insert(0, message)  # 反向添加
            elif hasattr(message.media, 'document') and message.media.document.mime_type == 'gif':  # 检查是否为 GIF 图片
                # 将 GIF 图片转换为视频文件
                gif_data = await message.download_media()
                gif_image = Image.open(io.BytesIO(gif_data))
                gif_image.seek(0)  # 确保在第一帧
                gif_image.save('temp.gif', save_all=True)
                video = await client.upload_file('temp.gif', part_size_kb=512)
                media.insert(0, video)  # 反向添加
            elif hasattr(message.media, 'document'):
                media.insert(0, message)  # 反向添加

        # 获取处理后的最终标题
        if switch_caption:
            caption = process_caption(messages)
            # caption = ''
        else:
            caption = None
            caption = messages[0].text if messages[0].text else None

        # 添加标签
        if switch_string:
            if caption is None:
                caption = ""
            if global_string.strip() not in caption:
                caption += global_string  # 只有当不在时才添加

            #添加序号
            global NUMBER_COUNT
            if switch_number:
                caption += f'\n{NUMBER_COUNT}'
                NUMBER_COUNT += 1 #序号

        # TG超链接
        if switch_TT_link:
            if caption is None:
                caption = ""
            caption = caption + global_TT_link

        if caption is not None and len(caption) > MAX_LENGTH:
            caption = caption[:MAX_LENGTH]

        if media:
            try:
                # 发送相册
                try:
                    await client.send_file(target, media, caption=caption)  # 无连接发送，发送三四千资源后需要等待,上面调用有错误提示;
                except WorkerBusyTooLongRetryError:
                    print("Telegram workers 太忙了，稍后重试")
                    await asyncio.sleep(5)
                    await client.send_file(target, media, caption=caption)  # 无连接发送，发送三四千资源后需要等待,上面调用有错误提示;

                # 转发完成后，将 ID 写入文件
                save_forwarded_ids(message_document_video_ids)
                save_forwarded_hash_ids(message_document_hash_ids)

            except telethon.errors.rpcerrorlist.MediaEmptyError as e:
                print("telethon.errors.rpcerrorlist.MediaEmptyError")


async def download_file(message, download_dir, sem):
    """下载单个媒体文件"""
    async with sem:  # 使用信号量限制并发下载
        try:
            if message is None:
                print("message 是 None，无法下载媒体")
            elif hasattr(message.media, 'photo') or "image" in message.media.document.mime_type:
                # 下载照片
                photo_path = os.path.join(download_dir, f"{message.id}_photo.jpg")
                await message.download_media(file=photo_path)
                print(f"[{message.id}] Photo saved at: {photo_path}")

            elif hasattr(message.media, 'video') or "video" in message.media.document.mime_type:
                # 下载视频
                video_path = os.path.join(download_dir, f"{message.id}_video.mp4")
                await message.download_media(file=video_path)
                print(f"[{message.id}] Video saved at: {video_path}")

            elif hasattr(message.media, 'document') and message.media.document.mime_type == 'gif':
                # 下载 GIF 并转换为视频文件（可选）
                gif_path = os.path.join(download_dir, f"{message.id}_gif.gif")
                await message.download_media(file=gif_path)
                print(f"[{message.id}] GIF saved at: {gif_path}")

                # 可选：将 GIF 转换为视频
                gif_image = Image.open(gif_path)
                gif_image.seek(0)  # 确保在第一帧
                video_gif_path = os.path.join(download_dir, f"{message.id}_gif_converted.mp4")
                gif_image.save(video_gif_path)
                print(f"[{message.id}] GIF converted to video and saved at: {video_gif_path}")

            elif hasattr(message.media, 'document'):
                # 下载其他文档类型
                document_path = os.path.join(download_dir,
                                             f"document_{message.id}.{message.media.document.mime_type.split('/')[-1]}")
                await message.download_media(file=document_path)
                print(f"[{message.id}] Document saved at: {document_path}")

        except Exception as e:
            print(f"Error downloading message {message.id}: {e}")

async def save_telegraph_links(telegraph_url, target="telegraph_links.txt"):
        links = re.findall(r"https?://telegra\.ph/\S+", telegraph_url)
        if links:
            with open(target, "a", encoding="utf-8") as f:
                for link in links:
                    f.write(link + "\n")
            print(f"[√] 已保存 {len(links)} 个 telegraph 链接 ")


async def download_media_group(messages, title, target, max_concurrent_downloads=5):
    """并发下载媒体文件"""
    # 创建保存媒体文件的目录
    download_dir = config["download_media"]["download_dir"]
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    sem = asyncio.Semaphore(max_concurrent_downloads)  # 限制并发下载数量
    download_tasks = []

    for message in reversed(messages):
        download_tasks.append(download_file(message, download_dir, sem))

    # 并发执行所有下载任务
    if download_tasks:
        await asyncio.gather(*download_tasks)


# 运行主函数
if __name__ == "__main__":
    # 设置开关变量
    switch_account = True  # True 表示清空并更换开发账号，False 表示使用原来的缓存 client
    asyncio.run(main())
    print("Final forwarded ID:", final_forwarded_id)

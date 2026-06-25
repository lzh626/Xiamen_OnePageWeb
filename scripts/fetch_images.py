import os
import shutil
import glob
import time
from icrawler.builtin import BaiduImageCrawler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(BASE_DIR, "frontend", "images")
REAL_DIR = os.path.join(IMG_DIR, "real")
os.makedirs(REAL_DIR, exist_ok=True)

ATTRACTIONS = {
    "gulangyu": "厦门鼓浪屿 日光岩 万国建筑 实景照片",
    "xiada": "厦门大学 芙蓉湖 嘉庚建筑 校园风景",
    "huandaolu": "厦门环岛路 海岸线 骑行道 马拉松",
    "nanputuo": "厦门南普陀寺 五老峰 寺庙建筑",
    "zengcuoan": "厦门曾厝垵 文艺渔村 小吃街",
    "shapowei": "厦门沙坡尾 渔港 艺术西区 避风坞",
    "zhongshanlu": "厦门中山路步行街 骑楼 夜景",
    "hulishan": "厦门胡里山炮台 克虏伯大炮 海景",
    "jimeixuecun": "厦门集美学村 龙舟池 嘉庚建筑",
    "yuanboyuan": "厦门园博苑 水上园林 花卉",
    "wuyuanwan": "厦门五缘湾湿地公园 黑天鹅",
    "tielugongyuan": "厦门铁路文化公园 三角梅 隧道",
    "dongpingshan": "厦门东坪山 山海健康步道 全景",
    "haicangdaqiao": "厦门海沧大桥 跨海大桥",
    "haicangwan": "厦门海沧湾公园 红树林 海岸",
}

MIN_SIZE = 2048


def valid_jpg(path):
    if not os.path.exists(path):
        return False
    if os.path.getsize(path) < MIN_SIZE:
        return False
    with open(path, "rb") as f:
        return f.read(3) == b"\xff\xd8\xff"


success = 0
skip = 0
fail = 0

for name, keyword in ATTRACTIONS.items():
    output_path = os.path.join(REAL_DIR, f"{name}.jpg")

    if valid_jpg(output_path):
        print(f"[SKIP] {name}.jpg  已存在且合法")
        skip += 1
        continue

    if os.path.exists(output_path):
        os.remove(output_path)

    temp_dir = os.path.join(REAL_DIR, f"_temp_{name}")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)
    os.makedirs(temp_dir, exist_ok=True)

    try:
        crawler = BaiduImageCrawler(
            parser_threads=2,
            downloader_threads=2,
            storage={"root_dir": temp_dir},
        )
        crawler.crawl(
            keyword=keyword,
            max_num=3,
            min_size=(400, 300),
            file_idx_offset=0,
        )

        jpgs = glob.glob(os.path.join(temp_dir, "*.jpg"))
        if not jpgs:
            jpgs = glob.glob(os.path.join(temp_dir, "*.*"))

        if not jpgs:
            print(f"[FAIL] {name}  未下载到图片 (关键词: {keyword})")
            fail += 1
            continue

        jpgs.sort(key=lambda f: os.path.getsize(f), reverse=True)
        best = jpgs[0]

        if os.path.getsize(best) < MIN_SIZE:
            print(f"[FAIL] {name}  图片过小 ({os.path.getsize(best)}B)")
            fail += 1
            continue

        shutil.move(best, output_path)
        print(f"[OK]   {name}.jpg  {os.path.getsize(output_path)}B  (关键词: {keyword})")
        success += 1

    except Exception as e:
        print(f"[FAIL] {name}  {e}")
        fail += 1
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        time.sleep(1.5)

print(f"\n===== 下载统计 =====")
print(f"成功: {success} | 跳过(已存在): {skip} | 失败: {fail}")
print(f"保存目录: {REAL_DIR}")

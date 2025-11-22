# -*- coding: utf-8 -*-
"""
双色球守号检测 + 冷号机选 + 企业微信&PushPlus 双推送（已加开奖日期）
"""

import requests
import random
import logging
from datetime import datetime
from collections import Counter

# ====================== 配置区 ======================
CONFIG = {
    "weixin": {
        "corpid": "",         # 企业ID
        "corpsecret": "",     # 应用Secret
        "touser": "@all",     # @all 或具体成员
        "agentid": ""         # 应用ID（字符串）
    },
    "pushplus": {
        "token": "你的PushPlus token"   # 必填
    }
}

# 你守的2注
FIXED_TICKETS = [
    {"red": [2, 15, 20, 21, 24, 26], "blue": 1},
    {"red": [3, 4, 11, 17, 23, 30], "blue": 6}
]

NUM_GENERATED = 2
HISTORY_LIMIT = 100

API_URL = "https://ms.zhcw.com/proxy/lottery-chart-center/history/SSQ"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ====================== 推送函数 ======================
def push_notification(contents: str):
    try:
        logger.info("开始发送推送通知")

        # 企业微信
        if all(CONFIG['weixin'].values()):
            token_resp = requests.get(
                f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?"
                f"corpid={CONFIG['weixin']['corpid']}&corpsecret={CONFIG['weixin']['corpsecret']}",
                timeout=10
            ).json()
            if token_resp.get('errcode') == 0:
                token = token_resp['access_token']
                payload = {
                    "touser": CONFIG['weixin']['touser'],
                    "msgtype": "text",
                    "agentid": CONFIG['weixin']['agentid'],
                    "text": {"content": "双色球开奖通知\n" + contents}
                }
                resp = requests.post(
                    f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}",
                    json=payload, timeout=10
                ).json()
                logger.info("企业微信推送成功" if resp['errmsg'] == 'ok' else f"企业微信失败: {resp}")

        # PushPlus
        if CONFIG['pushplus']['token']:
            payload = {
                "token": CONFIG['pushplus']['token'],
                "title": "双色球开奖通知",
                "content": contents.replace('\n', '<br>'),
                "template": "html"
            }
            resp = requests.post("http://www.pushplus.plus/send", json=payload, timeout=10).json()
            logger.info("PushPlus推送成功" if resp['code'] == 200 else f"PushPlus失败: {resp}")

        logger.info("所有推送完成")
    except Exception as e:
        logger.error(f"推送异常: {e}")

# ====================== 数据获取 ======================
def get_latest_and_history():
    headers = {"Content-Type": "application/json",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    payload = {"limit": HISTORY_LIMIT, "page": 1, "params": {}}

    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        datas = resp.json()["datas"]
        latest = datas[0]

        red_str = latest["winningFrontNum"]
        blue_str = latest["winningBackNum"]
        period = latest.get("issue", "未知")
        date = latest.get("openDate", "")[:10]   # 开奖日期

        latest_red = sorted(int(x) for x in red_str.split())
        latest_blue = int(blue_str)

        red_hist = [entry["winningFrontNum"].split() for entry in datas]
        blue_hist = [int(entry["winningBackNum"]) for entry in datas]

        return {
            "period": period,
            "date": date,
            "red": latest_red,
            "blue": latest_blue
        }, red_hist, blue_hist

    except Exception as e:
        logger.error(f"获取开奖数据失败: {e}")
        return None, None, None

# ====================== 中奖判断 & 冷号机选 ======================
def check_prize(tr, tb, wr, wb):
    rh = len(set(tr) & set(wr))
    bh = 1 if tb == wb else 0
    if rh == 6 and bh: return "★★★★★ 一等奖 5亿到手！！！ ★★★★★"
    if rh == 6: return "二等奖！已经起飞！"
    if rh == 5 and bh: return "三等奖！赚大了！"
    if rh == 5 or (rh == 4 and bh): return "四等奖"
    if rh == 4 or (rh == 3 and bh): return "五等奖"
    if bh: return "六等奖（蓝球中）"
    return "未中奖，继续守号~"

def generate_cold(red_hist, blue_hist):
    red_all = [int(n) for sub in red_hist for n in sub]
    red_c = Counter(red_all)
    blue_c = Counter(blue_hist)

    cold_red = [n for n, _ in sorted(red_c.items(), key=lambda x: x[1])[:18]]
    cold_blue = [n for n, _ in sorted(blue_c.items(), key=lambda x: x[1])[:10]]

    reds = sorted(random.sample(cold_red if len(cold_red) >= 6 else list(range(1,34)), 6))
    blue = random.choice(cold_blue if cold_blue else list(range(1,17)))
    return reds, blue

# ====================== 主程序 ======================
def main():
    print(f"\n{'='*30} 双色球监测+机选 {datetime.now().strftime('%Y-%m-%d %H:%M')} {'='*30}")

    result, r_hist, b_hist = get_latest_and_history()
    if not result:
        push_notification("【双色球】获取最新开奖数据失败，请检查网络或接口")
        return

    # 这里把开奖日期加进去了
    lines = [
        f"双色球 {result['period']} 已开奖！",
        f"开奖日期：{result['date']}",          # ← 新增这一行
        f"开奖号码：{' '.join(f'{x:02d}' for x in result['red'])} + {result['blue']:02d}",
        ""
    ]

    # 守号检测
    for i, t in enumerate(FIXED_TICKETS, 1):
        prize = check_prize(t["red"], t["blue"], result["red"], result["blue"])
        rs = ' '.join(f'{x:02d}' for x in sorted(t["red"]))
        print(f"守号第{i}注：{rs} + {t['blue']:02d} → {prize}")
        lines.append(f"守号第{i}注：{rs} + {t['blue']:02d}")
        lines.append(f"   → {prize}")
        lines.append("")

    # 冷号机选
    lines.append("今日冷号机选推荐：")
    for i in range(NUM_GENERATED):
        r, b = generate_cold(r_hist, b_hist)
        rs = ' '.join(f'{x:02d}' for x in r)
        print(f"机选第{i+1}注：{rs} + {b:02d}")
        lines.append(f"{rs} + {b:02d}")

    push_notification("\n".join(lines))
    print("\n推送已发送（含开奖日期），祝好运连连！")

if __name__ == "__main__":
    main()

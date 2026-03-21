#!/usr/bin/python3
# -- coding: utf-8 -- 
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/only_for_happly
# @Time : 2026/3/21 9:23
# -------------------------------
# cron "15 15 15 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('卡萨帝抽奖')
# 青龙变量HAIER_AK  地址  #小程序://海尔商城/VUSP0FXsbQ8y0Nr 点进去顺便助力一下 然后抓取请求头ak的值
import requests
import json
import time
import os

# --- 配置区 ---
# PushPlus Token (也可以设为环境变量 PUSH_PLUS_TOKEN)
PUSH_PLUS_TOKEN = os.getenv("PUSH_PLUS_TOKEN", "")


def push_plus(content):
    if not PUSH_PLUS_TOKEN:
        return
    url = "http://www.pushplus.plus/send"
    data = {
        "token": PUSH_PLUS_TOKEN,
        "title": "海尔抽奖结果通知",
        "content": content
    }
    try:
        requests.post(url, data=json.dumps(data), timeout=10)
    except Exception as e:
        print(f"推送失败: {e}")


def do_draw(index, ak):
    url = "https://m.ehaier.com/v4/mstore/sg/drawActivity/draw.json"

    headers = {
        "ak": ak,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254173b) XWEB/19027",
        "Content-Type": "application/json"
    }

    payload = {
        "activityCode": "74a4e11804164e2aba99f6793098fd5b"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                data = result.get("data", {})
                prize_name = data.get("prizeName")
                if prize_name:
                    msg = f"账号[{index}] 抽中奖品: {prize_name}"
                    print(f"[{time.strftime('%H:%M:%S')}] {msg}")
                    return msg
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] 账号[{index}] 未中奖")
            else:
                print(f"账号[{index}] 失败: {result.get('message')}")
        else:
            print(f"账号[{index}] 网络错误: {response.status_code}")
    except Exception as e:
        print(f"账号[{index}] 运行异常: {e}")
    return None


if __name__ == "__main__":
    # 从环境变量获取 AK，多个账号用 & 或 换行 分隔
    ak_env = os.getenv("HAIER_AK", "")

    if not ak_env:
        print("未检测到环境变量 HAIER_AK，请在青龙面板中配置。")
        exit(0)

    # 兼容换行或 & 分隔
    ak_list = ak_env.replace('\n', '&').split('&')
    ak_list = [i.strip() for i in ak_list if i.strip()]

    print(f"--- 检测到 {len(ak_list)} 个账号 ---")

    success_msgs = []
    for idx, ak in enumerate(ak_list, 1):
        res = do_draw(idx, ak)
        if res:
            success_msgs.append(res)
        # 账号间随机延迟，防止黑号
        time.sleep(2)

    # 如果有中奖信息，则发送推送
    if success_msgs:
        push_plus("\n".join(success_msgs))

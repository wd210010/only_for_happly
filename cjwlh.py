#!/usr/bin/python3
# -- coding: utf-8 -- 
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/only_for_happly
# @Time : 2026/04/16 9:23
# -------------------------------
# const $ = new Env('春茧未来荟')
# -*- coding: utf-8 -*-
#环境变量  #小程序://未来荟/8bPVJfkLSuIsvlx 打开 抓取Authorization

"""
cron: 30 8 * * *
new Env('华润置地签到查询');
"""

import os
import requests
import json

def start():
    # 1. 从环境变量获取 Authorization
    auth = os.getenv("CRLAND_AUTH")
    if not auth:
        print("❌ 未找到环境变量 CRLAND_AUTH，请先在青龙面板中设置。")
        return

    # 基本配置
    project_uuid = "3a59e62a07f811f1bec0aeefcf2e061a"
    app_id = "wx020209beec4251e0"
    
    headers = {
        "Host": "wlhmobile.crland.com.cn",
        "appId": app_id,
        "Authorization": auth,
        "projectUuid": project_uuid,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI",
        "Referer": f"https://servicewechat.com/{app_id}/29/page-frame.html",
    }

    payload = {
        "custom": {"catch": True},
        "projectUuid": project_uuid
    }

    # --- 步骤 1: 执行签到 ---
    sign_url = "https://wlhmobile.crland.com.cn/marketing/client/task/daily/sign-in"
    try:
        print("🔔 [签到模块] 正在尝试签到...")
        res_sign = requests.post(sign_url, headers=headers, json=payload, timeout=15).json()
        if res_sign.get("code") == 200:
            print(f"✅ 签到反馈: {res_sign.get('result')}")
        else:
            print(f"ℹ️ 签到反馈: {res_sign.get('text')} (可能是今日已签过)")
    except Exception as e:
        print(f"❌ 签到接口异常: {str(e)}")

    print("-" * 30)

    # --- 步骤 2: 执行查询 ---
    record_url = "https://wlhmobile.crland.com.cn/marketing/client/task/sign-in/record"
    try:
        print("🔍 [查询模块] 正在获取详细状态...")
        res_record = requests.post(record_url, headers=headers, json=payload, timeout=15).json()
        
        if res_record.get("code") == 200:
            data = res_record.get("result", {})
            
            # 提取关键信息
            is_signed = "已签到" if data.get("isSignedToday") else "未签到"
            count = data.get("currentCycleSignInCount", 0)
            reward = data.get("rewardPoint", 0)
            last_date = data.get("lastSignInDate", "无记录")
            
            print(f"📊 当前状态: {is_signed}")
            print(f"📅 本周期已连续签到: {count} 天")
            print(f"💰 今日获得积分: {reward}")
            print(f"⏰ 最后签到时间: {last_date}")
        else:
            print(f"❌ 查询失败: {res_record.get('text')}")
            
    except Exception as e:
        print(f"❌ 查询接口异常: {str(e)}")

if __name__ == "__main__":
    start()

# -*- coding: utf-8 -*-
import requests
import time
import os
import random
import urllib.parse
from requests.exceptions import RequestException

# ==============================================================================
# 【环境变量QH配置说明】
# 1. 格式：
#    - 单账号：直接填写wid（例：123456）
#    - 多账号：支持两种分隔方式，可混合使用
#      - &分隔：123&456&789
#      - 换行分隔：每个wid单独占一行（Windows/Linux换行符均兼容）
# 2. 关键：脚本仅内部使用wid登录，所有输出不显示wid；UA自动生成（适配小程序）
'''
不用抓包，直接登录小程序。
个人中心---用户设置---用户编号就是需要的wid信息
'''
# ==============================================================================
# -------------------------- 【配置+工具函数】--------------------------
def generate_random_ua():
    """生成随机UA（适配小程序环境）"""
    os_mobile_map = [
        ("15_8_3", "15E148"),
        ("16_2_0", "16F203"),
        ("16_5_1", "16H62"),
        ("17_0_3", "17A5844a"),
        ("17_1_1", "17B100"),
        ("17_2_0", "17C304"),
        ("17_3_1", "17D50"),
        ("17_4_1", "17E262"),
        ("17_6_1", "15E148")
    ]
    os_version, mobile_version = random.choice(os_mobile_map)
    wechat_version = f"8.0.{random.randint(50, 75)}"
    return (
        f"Mozilla/5.0 (iPhone; CPU iPhone OS {os_version} like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        f"Mobile/{mobile_version} MicroMessenger/{wechat_version} "
        "NetType/WIFI Language/zh_CN miniProgram/wx532ecb3bdaaf92f9"
    )

def parse_qh_env():
    """解析QH环境变量（支持&和换行分隔多账号）"""
    qh_env = os.getenv("QH", "")
    if not qh_env:
        print("❌ 错误：未检测到环境变量QH，请按配置说明设置！")
        return None
    
    unified_env = qh_env.replace("\r\n", "&").replace("\n", "&")
    account_str_list = unified_env.split("&")
    
    accounts = []
    for idx, account_str in enumerate(account_str_list, 1):
        wid = account_str.strip()
        if not wid:
            print(f"⚠️  检测到第{idx}个无效项（空内容），已跳过")
            continue
        
        ua = generate_random_ua()
        accounts.append({
            "index": idx, 
            "wid": wid, 
            "token": "", 
            "ua": ua,
            "user_data": {}, 
            "land_data": []
        })
    
    if not accounts:
        print("❌ 没有可用账号（所有项格式错误或为空），脚本终止")
        return None
    return accounts

def get_account_headers(account):
    """生成账号请求头（匹配抓包标准）"""
    headers = {
        "Authorization": account["token"],
        "User-Agent": account["ua"],
        "Origin": "https://h5.zhumanito.cn",
        "Referer": "https://h5.zhumanito.cn/",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    # 补充Cookie标识，模拟真实用户
    if account.get("wid"):
        headers["Cookie"] = f"rprm_cuid={account['wid']}; rprm_uuid={account['wid']}"
    return headers

def login_account(account):
    """账号自动登录（隐藏wid显示）"""
    login_url = "https://api.zhumanito.cn/api/login"
    headers = get_account_headers(account)
    headers["Content-Type"] = "application/json;charset=utf-8"
    payload = {"wid": account["wid"]}
    
    try:
        print(f"🔐 账号{account['index']}：发起登录请求")
        response = requests.post(login_url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        res = response.json()
        
        if res.get("code") != 200:
            print(f"❌ 账号{account['index']}：登录失败，原因：{res.get('msg', '未知错误')}")
            return False
        
        account["token"] = res["data"]["token"]
        account["user_data"] = res["data"]["user"]
        account["land_data"] = res["data"].get("land", [])
        
        print(f"✅ 账号{account['index']}：登录成功！")
        print(f"  📌 当前资源：💧{account['user_data']['water_num']}，☀️{account['user_data']['sun_num']}，🍀{account['user_data']['seed_num']}，🍎{account['user_data']['fruit_num']}")
        if account["land_data"]:
            print(f"  🌱 土地状态：共{len(account['land_data'])}块，生长阶段{account['land_data'][0]['seed_stage']}")
        return True
    
    except RequestException as e:
        print(f"❌ 账号{account['index']}：登录异常，原因：{str(e)}")
        return False

def get_user_status(account):
    """获取账号当前资源（水、阳光、种子、果实）"""
    if not account.get("user_data"):
        print(f"⚠️  账号{account['index']}：未获取到用户数据，返回默认资源值0")
        return 0, 0, 0, 0
    water = account["user_data"].get("water_num", 0)
    sun = account["user_data"].get("sun_num", 0)
    seed = account["user_data"].get("seed_num", 0)
    fruit = account["user_data"].get("fruit_num", 0)
    return water, sun, seed, fruit

def check_land_mature(account):
    """检查土地是否成熟（seed_stage=0 或 5 判定为可收获/可播种）"""
    if not account.get("land_data"):
        print(f"⚠️  账号{account['index']}：未获取到土地数据，默认判定为未成熟")
        return False
    return any(land["seed_stage"] in (0, 5) for land in account["land_data"])

# -------------------------- 【核心操作函数】--------------------------
def complete_harvest(headers, account_idx, account):
    """执行收获操作（支持seed_stage=0/5成熟阶段）"""
    harvest_url = "https://api.zhumanito.cn/api/harvest"
    try:
        mature_stages = [land["seed_stage"] for land in account["land_data"] if land["seed_stage"] in (0, 5)]
        print("=" * 35)
        print(f"🍎 账号{account_idx}：开始执行收获操作（成熟阶段：{mature_stages}）")
        harvest_headers = headers.copy()
        harvest_headers["Content-Type"] = "application/x-www-form-urlencoded;charset=utf-8"
        
        response = requests.post(harvest_url, headers=harvest_headers, data=b"", timeout=(25, 30))
        response.raise_for_status()
        res = response.json()
        
        if res.get("code") != 200:
            print(f"❌ 账号{account_idx}：收获失败，原因：{res.get('msg', '未知错误')}")
            return False
        
        account["user_data"] = res["data"]["user"]
        account["land_data"] = res["data"].get("land", [])
        
        current_water, current_sun, current_seed, current_fruit = get_user_status(account)
        land_count = len(account["land_data"])
        print(f"✅ 账号{account_idx}：收获成功！")
        print(f"📊 收获后资源：💧{current_water}，☀️{current_sun}，🍀{current_seed}，🍎{current_fruit}")
        if land_count > 0:
            print(f"🌱 土地状态：共{land_count}块，当前阶段{account['land_data'][0]['seed_stage']}")
        print("=" * 35)
        return True
    
    except RequestException as e:
        print(f"❌ 账号{account_idx}：收获异常，原因：{str(e)}")
        return False

def complete_seed(headers, account_idx, account):
    """执行播种操作（无重试）"""
    seed_url = "https://api.zhumanito.cn/api/seed"
    _, _, current_seed, _ = get_user_status(account)
    if current_seed < 1:
        print(f"⚠️  账号{account_idx}：种子数量不足（当前🍀{current_seed}），无法播种")
        return False
    
    try:
        print("=" * 35)
        print(f"🌱 账号{account_idx}：开始执行播种操作（当前种子：🍀{current_seed}）")
        seed_headers = headers.copy()
        seed_headers["Content-Type"] = "application/x-www-form-urlencoded;charset=utf-8"
        
        response = requests.post(seed_url, headers=seed_headers, data=b"", timeout=(25, 30))
        response.raise_for_status()
        res = response.json()
        
        if res.get("code") != 200:
            print(f"❌ 账号{account_idx}：播种失败，原因：{res.get('msg', '未知错误')}")
            return False
        
        account["user_data"] = res["data"]["user"]
        account["land_data"] = res["data"]["land"]
        
        current_water, current_sun, new_seed, current_fruit = get_user_status(account)
        land_count = len(account["land_data"])
        print(f"✅ 账号{account_idx}：播种成功！")
        print(f"📊 播种后资源：💧{current_water}，☀️{current_sun}，🍀{new_seed}，🍎{current_fruit}")
        print(f"🌱 土地状态：共{land_count}块，生长阶段{account['land_data'][0]['seed_stage']}")
        print("=" * 35)
        return True
    
    except RequestException as e:
        print(f"❌ 账号{account_idx}：播种异常，原因：{str(e)}")
        return False

# -------------------------- 【主流程】--------------------------
def auto_multi_account():
    """多账号自动处理主流程：登录→检测成熟→收获→播种"""
    accounts = parse_qh_env()
    if not accounts:
        return
    
    for account in accounts:
        account_idx = account["index"]
        total_accounts = len(accounts)
        print(f"\n" + "=" * 35)
        print(f"📌 正在处理账号 {account_idx}/{total_accounts}")
        print("=" * 35)
        
        # 1. 账号登录
        login_success = login_account(account)
        if not login_success:
            print(f"❌ 账号{account_idx}：登录失败，跳过后续所有操作")
            continue
        
        # 2. 获取请求头
        account_headers = get_account_headers(account)
        
        # 3. 收获→播种流程
        print(f"\n🔄 账号{account_idx}：进入收获→播种流程")
        
        # 3.1 检测土地成熟度并收获
        if check_land_mature(account):
            print(f"\n📌 账号{account_idx}：检测到土地成熟，执行收获")
            harvest_success = complete_harvest(account_headers, account_idx, account)
            if harvest_success:
                time.sleep(2)
        else:
            print(f"\n📌 账号{account_idx}：土地未成熟，跳过收获")
        
        # 3.2 播种（种子≥1且土地可播种）
        _, _, current_seed, _ = get_user_status(account)
        if current_seed >= 1 and check_land_mature(account):
            print(f"\n📌 账号{account_idx}：种子充足且土地可播种，执行播种")
            complete_seed(account_headers, account_idx, account)
        else:
            print(f"\n📌 账号{account_idx}：种子不足（🍀{current_seed}）或土地不可播种，跳过播种")
        
        # 单个账号处理完成
        print(f"\n✅ 账号{account_idx}/{total_accounts}：收获播种流程处理完毕")
        if account_idx < total_accounts:
            delay_time = 5
            print(f"⏳ 账号间延迟{delay_time}秒，准备处理下一个账号...\n")
            time.sleep(delay_time)
    
    # 所有账号处理完成
    print("\n" + "=" * 35)
    print("🎯 所有账号收获播种流程已全部处理完成！脚本执行结束")
    print("=" * 35)

# 脚本入口
if __name__ == "__main__":
    try:
        auto_multi_account()
    except KeyboardInterrupt:
        print(f"\n" + "=" * 35)
        print("⚠️  脚本被手动终止")
        print("=" * 35)

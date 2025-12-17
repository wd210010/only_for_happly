import requests
import json
import os
import time
import re
import random
from collections import defaultdict
from typing import Dict, List, Optional, Any, Tuple
from notify import send

# ==================== 配置项 ====================
# 环境变量名称 抓包小程序wid即可
ENV_KEY = "TYQH"
# 请求超时时间（秒）
REQUEST_TIMEOUT = 15
# 基础等待时间范围（秒）
BASE_WAIT_RANGE = (4, 5)
# 账号间等待时间（秒）
ACCOUNT_INTERVAL = 3
# 浇水最大重试次数
WATER_MAX_RETRY = 3
# API基础配置
API_BASE_URL = "https://api.zhumanito.cn/api"
# User-Agent配置
USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 14; 23046RP50C Build/UKQ1.230804.001; wv) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/142.0.7444.172 "
    "Safari/537.36 XWEB/1420045 MMWEBSDK/20250201 MMWEBID/5714 "
    "MicroMessenger/8.0.57.2820(0x28003956) WeChat/arm64 Weixin Android Tablet "
    "NetType/WIFI Language/zh_CN ABI/arm64 miniProgram/wx532ecb3bdaaf92f9"
)

# 步骤配置
STEP_CONFIG = {
    "login": {"name": "登录", "emoji": "🔑"},
    "get_seeds": {"name": "领取种子", "emoji": "🌱"},
    "check_in": {"name": "签到", "emoji": "📅"},
    "explore": {"name": "浏览任务", "emoji": "🔍"},
    "harvest": {"name": "收获作物", "emoji": "🌾"},
    "plant_seed": {"name": "播种", "emoji": "🌱"},
    "watering": {"name": "循环浇水", "emoji": "🔄"},
    "info": {"name": "信息", "emoji": "•"}
}
STEP_ORDER = [v["name"] for k, v in STEP_CONFIG.items() if k != "info"] + [STEP_CONFIG["info"]["name"]]

# 状态图标
STATUS_ICONS = {
    "success": "✅",
    "warning": "⚠️",
    "error": "❌",
    "info": "ℹ️"
}

# ==================== 工具函数 ====================
def short_text(text: str, max_length: int = 120) -> str:
    """截断文本并添加省略号"""
    text = text.strip()
    return text if len(text) <= max_length else f"{text[:max_length-1]}…"

def extract_status(text: str) -> str:
    """提取状态图标"""
    if STATUS_ICONS["success"] in text:
        return STATUS_ICONS["success"]
    elif STATUS_ICONS["warning"] in text:
        return STATUS_ICONS["warning"]
    elif STATUS_ICONS["error"] in text:
        return STATUS_ICONS["error"]
    return STATUS_ICONS["info"]

def get_step_key(text: str) -> str:
    """获取步骤名称"""
    for step_name in STEP_ORDER:
        if step_name in text:
            return step_name
    return STEP_CONFIG["info"]["name"]

def extract_resource_snapshot(lines: List[str]) -> Dict[str, int]:
    """提取资源快照（阳光、水、番茄）"""
    resources = {}
    patterns = {
        "sun": r"☀️(\d+)",
        "water": r"💧(\d+)",
        "fruit": r"🍅(\d+)"
    }
    
    for line in reversed(lines):
        for res_type, pattern in patterns.items():
            if res_type in resources:
                continue
                
            match = re.search(pattern, line)
            if match:
                try:
                    resources[res_type] = int(match.group(1))
                except (ValueError, IndexError):
                    pass
        
        if len(resources) >= 2:
            break
    
    return resources

def render_report(all_lines: List[str]) -> str:
    """渲染执行报告"""
    # 按用户分组
    blocks = []
    current_block = []
    
    for line in all_lines:
        if line.strip().startswith("👤 用户"):
            if current_block:
                blocks.append(current_block)
            current_block = [line.strip()]
        elif line is not None and line.strip():
            current_block.append(line.rstrip())
    
    if current_block:
        blocks.append(current_block)
    
    # 生成报告内容
    report_lines = []
    for block in blocks:
        if not block:
            continue
            
        # 添加分隔线和用户信息
        report_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        report_lines.append(block[0])
        
        # 按步骤分类日志
        step_buckets = defaultdict(list)
        for line in block[1:]:
            step_key = get_step_key(line)
            step_buckets[step_key].append(line)
        
        # 添加资源快照
        resource_snap = extract_resource_snapshot(block)
        if resource_snap:
            resource_line = "📊 当前资源："
            if "sun" in resource_snap:
                resource_line += f"☀️{resource_snap['sun']}  "
            if "water" in resource_snap:
                resource_line += f"💧{resource_snap['water']}  "
            if "fruit" in resource_snap:
                resource_line += f"🍅{resource_snap['fruit']}  "
            report_lines.append(resource_line.strip())
        
        # 添加各步骤执行结果
        for step in STEP_ORDER:
            if step not in step_buckets:
                continue
                
            # 去重并清理日志行
            unique_lines = []
            seen = set()
            
            for line in step_buckets[step]:
                # 跳过分隔线
                if set(line.strip()) == set("="):
                    continue
                    
                normalized = re.sub(r"\s+", " ", line).strip()
                if normalized not in seen:
                    seen.add(normalized)
                    unique_lines.append(normalized)
            
            # 选择要显示的行（循环浇水显示所有，其他显示最后一条）
            display_lines = unique_lines if step == STEP_CONFIG["watering"]["name"] else unique_lines[-1:]
            
            # 添加到报告
            for line in display_lines:
                status = extract_status(line)
                emoji = next(v["emoji"] for k, v in STEP_CONFIG.items() if v["name"] == step)
                # 移除前缀
                clean_line = re.sub(
                    rf"^[{''.join(v['emoji'] for v in STEP_CONFIG.values())}]\s*{re.escape(step)}[:：]?\s*",
                    "", line
                )
                report_lines.append(f"{emoji} {step} {status}  {short_text(clean_line)}")
        
        # 添加小结
        success_count = sum(STATUS_ICONS["success"] in line for line in block)
        warning_count = sum(STATUS_ICONS["warning"] in line for line in block)
        error_count = sum(STATUS_ICONS["error"] in line for line in block)
        report_lines.append(f"🧾 小结：成功 {success_count} · 预警 {warning_count} · 失败 {error_count}")
    
    # 添加结束分隔线
    report_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    
    return "\n".join(report_lines)

def random_sleep(min_seconds: float = None, max_seconds: float = None) -> None:
    """随机等待"""
    min_s = min_seconds or BASE_WAIT_RANGE[0]
    max_s = max_seconds or BASE_WAIT_RANGE[1]
    time.sleep(random.uniform(min_s, max_s))

def create_headers(auth_token: str = None, content_type: str = "application/json") -> Dict[str, str]:
    """创建请求头"""
    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": content_type
    }
    if auth_token:
        headers["Authorization"] = auth_token
    return headers

# ==================== 核心功能函数 ====================
def login_account(wid: str, user_logs: List[str]) -> Optional[Dict[str, Any]]:
    """
    登录账号
    :param wid: 用户ID
    :param user_logs: 日志列表
    :return: 登录数据字典或None
    """
    step = STEP_CONFIG["login"]["name"]
    emoji = STEP_CONFIG["login"]["emoji"]
    
    try:
        url = f"{API_BASE_URL}/login"
        payload = {"wid": wid}
        headers = create_headers()
        
        response = requests.post(
            url,
            data=json.dumps(payload),
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        
        result = response.json()
        
        # 检查登录结果
        if all(key in result.get("data", {}) for key in ["token", "user", "land"]):
            msg = "登录成功 ✅"
            user_logs.append(f"{emoji} {step}: {msg}")
            random_sleep()
            return {
                "token": result["data"]["token"],
                "user_data": result["data"]["user"],
                "land_data": result["data"]["land"]
            }
        else:
            msg = f"登录失败，返回数据不完整: {json.dumps(result, ensure_ascii=False)} ❌"
            user_logs.append(f"{emoji} {step}: {msg}")
            return None
            
    except requests.exceptions.RequestException as e:
        msg = f"登录请求出错: {str(e)} ❌"
        user_logs.append(f"{emoji} {step}: {msg}")
        return None
    except Exception as e:
        msg = f"登录处理出错: {str(e)} ❌"
        user_logs.append(f"{emoji} {step}: {msg}")
        return None

def collect_seeds(auth_token: str, user_logs: List[str]) -> None:
    """领取种子/引导任务"""
    step = STEP_CONFIG["get_seeds"]["name"]
    emoji = STEP_CONFIG["get_seeds"]["emoji"]
    
    if not auth_token:
        msg = "未获取到授权，无法领取种子 🔒"
        user_logs.append(f"{emoji} {step}: {msg}")
        return
    
    try:
        url = f"{API_BASE_URL}/guide"
        headers = create_headers(auth_token)
        
        # 执行引导步骤1和2
        for status in (1, 2):
            payload = {"status": status}
            response = requests.post(
                url,
                data=json.dumps(payload),
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
        
        msg = "领取/引导完成 ✅"
        user_logs.append(f"{emoji} {step}: {msg}")
        random_sleep()
        
    except requests.exceptions.RequestException as e:
        msg = f"领取种子请求出错: {str(e)} ❌"
        user_logs.append(f"{emoji} {step}: {msg}")
    except Exception as e:
        msg = f"领取种子处理出错: {str(e)} ❌"
        user_logs.append(f"{emoji} {step}: {msg}")

def do_check_in(auth_token: str, user_logs: List[str]) -> None:
    """签到"""
    step = STEP_CONFIG["check_in"]["name"]
    emoji = STEP_CONFIG["check_in"]["emoji"]
    
    if not auth_token:
        msg = "未获取到授权，无法签到 🔒"
        user_logs.append(f"{emoji} {step}: {msg}")
        return
    
    try:
        url = f"{API_BASE_URL}/task/complete"
        headers = create_headers(auth_token, "application/x-www-form-urlencoded")
        
        response = requests.post(
            url,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        result = response.json()
        
        # 处理签到结果
        msg = result.get("msg", "未知错误")
        if msg == "成功":
            status_msg = "签到成功 ✅"
        elif msg == "不可重复完成":
            status_msg = "今日已签到，无需重复操作 ✅"
        else:
            status_msg = f"失败，原因: {msg} ❌"
        
        user_logs.append(f"{emoji} {step}: {status_msg}")
        random_sleep()
        
    except requests.exceptions.RequestException as e:
        msg = f"签到请求出错: {str(e)} ❌"
        user_logs.append(f"{emoji} {step}: {msg}")
    except Exception as e:
        msg = f"签到处理出错: {str(e)} ❌"
        user_logs.append(f"{emoji} {step}: {msg}")

def browse_tasks(auth_token: str, wid: str, user_logs: List[str]) -> None:
    """浏览任务"""
    step = STEP_CONFIG["explore"]["name"]
    emoji = STEP_CONFIG["explore"]["emoji"]
    
    if not auth_token:
        msg = "未获取到授权，无法执行浏览任务 🔒"
        user_logs.append(f"{emoji} {step}: {msg}")
        return
    
    max_retry = 3
    retry_count = 0
    
    while retry_count < max_retry:
        try:
            url = f"https://api.zhumanito.cn/?wid={wid}"
            headers = {
                'Host': 'api.zhumanito.cn',
                'User-Agent': USER_AGENT,
                'Authorization': auth_token,
                'sec-ch-ua': '"Chromium";v="142", "Android WebView";v="142", "Not_A Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Android"',
                'upgrade-insecure-requests': '1',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/wxpic,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'x-requested-with': 'com.tencent.mm',
                'sec-fetch-site': 'same-site',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'referer': 'https://h5.zhumanito.cn/',
                'accept-encoding': 'gzip, deflate, br, zstd',
                'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'priority': 'u=0, i'
            }
            
            # 禁用重定向，手动处理302
            response = requests.get(
                url,
                headers=headers,
                allow_redirects=False,
                timeout=REQUEST_TIMEOUT,
                verify=True
            )
            
            if response.status_code == 302:
                msg = "浏览任务完成 ✅"
                user_logs.append(f"{emoji} {step}: {msg}")
                random_sleep()
                break
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "1"))
                retry_count += 1
                if retry_count < max_retry:
                    msg = f"浏览请求限速，等待{retry_after}秒后重试（第{retry_count}/{max_retry}次）"
                    user_logs.append(f"{emoji} {step}: {msg}")
                    time.sleep(retry_after)
                else:
                    msg = f"浏览请求多次限速，放弃重试 ❌"
                    user_logs.append(f"{emoji} {step}: {msg}")
            else:
                msg = f"浏览失败，状态码: {response.status_code} ❌"
                user_logs.append(f"{emoji} {step}: {msg}")
                break
                
        except requests.exceptions.RequestException as e:
            msg = f"浏览任务请求出错: {str(e)} ❌"
            user_logs.append(f"{emoji} {step}: {msg}")
            break
        except Exception as e:
            msg = f"浏览任务处理出错: {str(e)} ❌"
            user_logs.append(f"{emoji} {step}: {msg}")
            break

def harvest_crops(auth_token: str, user_logs: List[str], account: Dict[str, Any]) -> bool:
    """收获作物"""
    step = STEP_CONFIG["harvest"]["name"]
    emoji = STEP_CONFIG["harvest"]["emoji"]
    
    try:
        url = f"{API_BASE_URL}/harvest"
        headers = create_headers(auth_token, "application/x-www-form-urlencoded;charset=utf-8")
        
        # 记录收获前的番茄数量
        before_fruit = int(account["user_data"].get("fruit_num", 0))
        
        response = requests.post(
            url,
            headers=headers,
            data=b"",
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        result = response.json()
        
        if result.get("code") == 200:
            # 更新账号数据
            account["user_data"] = result["data"]["user"]
            account["land_data"] = result["data"]["land"]
            
            # 计算收获的番茄数量
            after_fruit = int(account["user_data"].get("fruit_num", 0))
            total_after = int(account["user_data"].get("total_fruit_num", after_fruit))
            delta = max(0, after_fruit - before_fruit)
            
            msg = f"收获成功！🍅+{delta} → 现有 {after_fruit}（累计 {total_after}）✅"
            user_logs.append(f"{emoji} {step}: {msg}")
            
            # 记录资源快照
            snap_msg = f"📊 收获后资源：☀️{account['user_data'].get('sun_num',0)}  💧{account['user_data'].get('water_num',0)}  🍅{after_fruit}"
            user_logs.append(snap_msg)
            
            random_sleep()
            return True
        else:
            msg = f"收获失败: {result.get('msg', '未知信息')} ⚠️"
            user_logs.append(f"{emoji} {step}: {msg}")
            return False
            
    except requests.exceptions.RequestException as e:
        msg = f"收获请求出错: {str(e)} ❌"
        user_logs.append(f"{emoji} {step}: {msg}")
        return False
    except Exception as e:
        msg = f"收获处理出错: {str(e)} ❌"
        user_logs.append(f"{emoji} {step}: {msg}")
        return False

def plant_seeds(auth_token: str, user_logs: List[str], account: Dict[str, Any]) -> bool:
    """播种"""
    step = STEP_CONFIG["plant_seed"]["name"]
    emoji = STEP_CONFIG["plant_seed"]["emoji"]
    
    try:
        url = f"{API_BASE_URL}/seed"
        headers = create_headers(auth_token, "application/x-www-form-urlencoded;charset=utf-8")
        
        response = requests.post(
            url,
            headers=headers,
            data=b"",
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        result = response.json()
        
        if result.get("code") == 200:
            msg = "播种成功！✅"
            user_logs.append(f"{emoji} {step}: {msg}")
            
            # 更新账号数据
            account["user_data"] = result["data"]["user"]
            account["land_data"] = result["data"]["land"]
            
            random_sleep()
            return True
        else:
            msg = f"播种失败: {result.get('msg', '未知信息')} ⚠️"
            user_logs.append(f"{emoji} {step}: {msg}")
            return False
            
    except requests.exceptions.RequestException as e:
        msg = f"播种请求出错: {str(e)} ❌"
        user_logs.append(f"{emoji} {step}: {msg}")
        return False
    except Exception as e:
        msg = f"播种处理出错: {str(e)} ❌"
        user_logs.append(f"{emoji} {step}: {msg}")
        return False

def water_once_request(headers: Dict[str, str], account_idx: int) -> Optional[Dict[str, Any]]:
    """单次浇水请求（带重试）"""
    retry_count = 0
    
    while retry_count < WATER_MAX_RETRY:
        try:
            response = requests.post(
                f"{API_BASE_URL}/water",
                headers=headers,
                data=b"",
                allow_redirects=False,
                timeout=(25, 30)
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "1"))
                retry_count += 1
                if retry_count < WATER_MAX_RETRY:
                    print(f"账号{account_idx}：浇水请求限速，等待{retry_after}秒后重试（第{retry_count}/{WATER_MAX_RETRY}次）")
                    time.sleep(retry_after)
                else:
                    raise Exception(f"浇水请求多次限速（{WATER_MAX_RETRY}次），放弃重试")
            else:
                raise Exception(f"响应状态码异常: {response.status_code}，内容: {response.text}")
                
        except json.JSONDecodeError:
            raise Exception(f"返回非JSON数据: {response.text}")
        except Exception as e:
            if retry_count >= WATER_MAX_RETRY - 1:
                raise e
            retry_count += 1
            time.sleep(1)
    
    return None

def loop_watering_process(headers: Dict[str, str], account_idx: int, 
                         account: Dict[str, Any], user_logs: List[str]) -> None:
    """循环浇水"""
    step = STEP_CONFIG["watering"]["name"]
    emoji = STEP_CONFIG["watering"]["emoji"]
    
    user_logs.append(f"{emoji} {step}：进入循环浇水（需💧≥20且☀️≥20）")
    print(f"\n{emoji} 账号{account_idx}：进入循环浇水（需💧≥20且☀️≥20）")
    
    # 准备浇水请求头
    water_headers = headers.copy()
    water_headers["Content-Type"] = "application/x-www-form-urlencoded;charset=UTF-8"
    
    while True:
        # 获取当前资源
        water = account["user_data"].get("water_num", 0)
        sun = account["user_data"].get("sun_num", 0)
        
        # 检查资源是否满足
        if water >= 20 and sun >= 20:
            log_msg = f"📌 账号{account_idx}：资源满足（💧{water}，☀️{sun}），浇水..."
            print(log_msg)
            user_logs.append(log_msg)
            
            try:
                # 执行浇水
                result = water_once_request(water_headers, account_idx)
                
                if result and result.get("code") == 200:
                    # 更新账号数据
                    account["user_data"] = result["data"]["user"]
                    
                    # 记录成功信息
                    success_msg = f"✅ 账号{account_idx}：浇水成功！"
                    status_msg = f"📊 剩余：💧{account['user_data']['water_num']}，☀️{account['user_data']['sun_num']}"
                    
                    print("="*35)
                    print(success_msg)
                    print(status_msg)
                    user_logs.append(success_msg)
                    user_logs.append(status_msg)
                    
                    # 记录土地状态
                    land = result["data"].get("land", [])
                    if land:
                        land_msg = f"🌱 土地：共{len(land)}块，阶段{land[0]['seed_stage']} 🌱"
                        print(land_msg)
                        user_logs.append(land_msg)
                    print("="*35)
                    
                    random_sleep()
                else:
                    # 浇水失败
                    fail_msg = f"❌ 账号{account_idx}：浇水失败：{result.get('msg', '未知错误') if result else '无响应'}"
                    print(fail_msg)
                    user_logs.append(f"{emoji} {step}：{fail_msg}")
                    break
                    
            except Exception as e:
                error_msg = f"⚠️ 账号{account_idx}：浇水请求异常：{str(e)} ❌"
                print(error_msg)
                user_logs.append(f"{emoji} {step}：{error_msg}")
                break
        else:
            # 资源不足，停止浇水
            end_msg = f"🔚 账号{account_idx}：资源不足（💧{water}，☀️{sun}），停止浇水 ⏹️"
            print(end_msg)
            user_logs.append(f"{STATUS_ICONS['info']} {step}：{end_msg}")
            
            # 记录最终资源
            fruit = account['user_data'].get('fruit_num', 0)
            final_snap = f"📊 最终资源：☀️{sun}  💧{water}  🍅{fruit}"
            print(final_snap)
            user_logs.append(final_snap)
            break

def process_single_user(wid: str, user_index: int) -> List[str]:
    """处理单个用户"""
    user_logs = [f"👤 用户{user_index}: {wid}"]
    print(f"\n===== 开始处理用户 {user_index} (wid: {wid}) =====")
    
    # 登录
    login_data = login_account(wid, user_logs)
    if not login_data:
        msg = "获取授权失败，无法执行后续操作 🔒"
        print(msg)
        user_logs.append(f"{STATUS_ICONS['warning']} {msg}")
        print(f"===== 完成处理用户 {user_index} =====\n")
        time.sleep(ACCOUNT_INTERVAL)
        return user_logs
    
    # 登录成功，继续处理
    auth_token = login_data["token"]
    headers = create_headers(auth_token)
    account = {
        "user_data": login_data["user_data"],
        "land_data": login_data["land_data"]
    }
    
    # 记录当前番茄数量
    fruit = account['user_data'].get('fruit_num', 0)
    print(f"📊 当前番茄数量：{fruit}")
    user_logs.append(f"📊 当前番茄数量：{fruit}")
    
    # 领取种子（如果是新用户）
    if account["user_data"].get("new_status", 2) != 2:
        collect_seeds(auth_token, user_logs)
    
    # 执行签到
    do_check_in(auth_token, user_logs)
    
    # 执行浏览任务
    browse_tasks(auth_token, wid, user_logs)
    
    # 智能判断土地状态
    current_stage = 0
    if account["land_data"] and len(account["land_data"]) > 0:
        current_stage = account["land_data"][0].get("seed_stage", 0)
    
    print(f"\n🧠 账号{user_index}：智能判断... 当前土地状态: {current_stage}")
    user_logs.append(f"{STATUS_ICONS['info']} 土地状态: {current_stage}")
    
    if current_stage == 5:
        print("判断：作物已成熟。")
        user_logs.append("🧠 判断：作物已成熟。")
        print(f">> 账号{user_index}：执行 [收获]...")
        harvest_success = harvest_crops(auth_token, user_logs, account)
        if harvest_success:
            print(f">> 账号{user_index}：执行 [播种]...")
            plant_seeds(auth_token, user_logs, account)
    elif current_stage == 0:
        print("判断：土地为空。")
        user_logs.append("🧠 判断：土地为空。")
        print(f">> 账号{user_index}：执行 [播种]...")
        plant_seeds(auth_token, user_logs, account)
    else:
        print("判断：作物生长中... 无需收获或播种。")
        user_logs.append("🧠 判断：作物生长中。")
    
    # 循环浇水
    loop_watering_process(headers, user_index, account, user_logs)
    
    print(f"===== 完成处理用户 {user_index} =====\n")
    time.sleep(ACCOUNT_INTERVAL)
    return user_logs

# ==================== 主程序 ====================
def main():
    """主函数"""
    # 获取用户列表
    users_str = os.getenv(ENV_KEY, "")
    users = [user.strip() for user in users_str.split("&") if user.strip()]
    
    if not users:
        error_msg = f"未从环境变量{ENV_KEY}中获取到任何用户信息！ 🚫"
        print(error_msg)
        send("统一茄皇", error_msg)
        return
    
    print(f"共检测到 {len(users)} 个用户，开始依次处理... 👥")
    
    # 处理所有用户
    all_logs = []
    for index, user_wid in enumerate(users, 1):
        try:
            user_logs = process_single_user(user_wid, index)
            all_logs.extend(user_logs)
            all_logs.append("")
        except Exception as e:
            error_msg = f"用户 {index} 处理过程中发生未捕获错误: {str(e)} ❌"
            print(error_msg)
            all_logs.append(f"{STATUS_ICONS['error']} {error_msg}")
            all_logs.append("")
    
    # 生成并发送报告
    report = render_report(all_logs)
    print("\n" + "="*50)
    print("执行报告：")
    print(report)
    print("="*50)
    
    send("统一茄皇", report)

if __name__ == "__main__":
    main()

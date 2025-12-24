#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/only_for_happly
# @Time : 2025/12/24 9:23
# -------------------------------
# cron "0 0 8 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('品赞签到')
# 变量名：Pzandaili ACCOUNT1#PASSWORD1@ACCOUNT2#PASSWORD2 或 & 分隔
# 品赞注册链接：https://www.ipzan.com?pid=b8quopmio
import warnings
import os
import random
import base64
import requests
import time
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

# -------------------------- 全局配置 --------------------------
# 基础URL配置
CONFIG_URLS = {
    "home": "https://www.ipzan.com?pid=b1sf3o4ao",
    "login": "https://service.ipzan.com/users-login",
    "receive": "https://service.ipzan.com/home/userWallet-receive"
}

# 环境变量配置
ENV_CONFIG = {
    "var_name": "Pzandaili",
    "separators": ["@", "&"],  # 多账户分隔符
    "fixed_key": "QWERIPZAN1290QWER"  # 加密固定密钥
}

# 请求配置
REQUEST_CONFIG = {
    "timeout": 15,
    "sleep_range": (2, 5),  # 多账户延迟范围
    "retry_times": 1,  # 接口重试次数
    "user_agents": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    ]
}

# 关闭SSL警告
warnings.filterwarnings("ignore")

# -------------------------- 数据结构定义 --------------------------
@dataclass
class AccountInfo:
    """账户信息数据类"""
    index: int
    account: str
    password: str

@dataclass
class ProcessResult:
    """账户处理结果数据类"""
    account_index: int
    account_masked: str
    status: str  # success/failed/duplicate/error
    message: str
    raw_data: Optional[Any] = None

# -------------------------- 工具函数 --------------------------
def get_random_user_agent() -> str:
    """获取随机User-Agent"""
    return random.choice(REQUEST_CONFIG["user_agents"])

def get_base_headers() -> Dict[str, str]:
    """获取基础请求头"""
    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://ipzan.com",
        "Referer": "https://ipzan.com/",
        "User-Agent": get_random_user_agent()
    }

def mask_account(account: str) -> str:
    """账号脱敏显示"""
    if len(account) > 7:
        return f"{account[:3]}****{account[-4:]}"
    return account[:2] + "****" + account[-1:] if len(account) > 3 else "****"

@contextmanager
def request_session():
    """请求会话上下文管理器，自动关闭会话"""
    session = requests.Session()
    try:
        session.headers.update(get_base_headers())
        yield session
    finally:
        session.close()

def retry_on_failure(max_retries: int = 1):
    """重试装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        sleep_time = random.uniform(1, 3)
                        print(f"⚠️ 尝试{attempt+1}失败，{sleep_time:.1f}秒后重试：{str(e)[:50]}")
                        time.sleep(sleep_time)
                    else:
                        raise e
            raise last_exception
        return wrapper
    return decorator

# -------------------------- 核心加密逻辑 --------------------------
def encrypt_account(phone: str, password: str) -> str:
    """IPZAN专属加密逻辑（官网JS还原）"""
    # 基础加密
    plain_text = f"{phone}{ENV_CONFIG['fixed_key']}{password}"
    encoded_str = base64.b64encode(plain_text.encode("utf-8")).decode("utf-8")
    
    # 生成400位混淆字符串
    random_hex = []
    for _ in range(80):
        hex_str = hex(int(random.random() * 10**16))[2:]
        random_hex.append(hex_str)
    random_hex = "".join(random_hex).ljust(400, "0")[:400]
    
    # 分段拼接
    parts = [
        random_hex[:100], encoded_str[:8],
        random_hex[100:200], encoded_str[8:20],
        random_hex[200:300], encoded_str[20:],
        random_hex[300:400]
    ]
    return "".join(parts)

# -------------------------- 账户加载 --------------------------
def load_accounts_from_env() -> List[AccountInfo]:
    """加载环境变量中的账户信息，返回结构化的账户列表"""
    env_value = os.getenv(ENV_CONFIG["var_name"])
    
    if not env_value:
        raise ValueError(
            f"❌ 环境变量 {ENV_CONFIG['var_name']} 未设置！\n"
            f"📝 配置格式参考：\n"
            f"  - 单账户：账号#密码\n"
            f"  - 多账户：账号1#密码1@账号2#密码2（或&分隔）"
        )
    
    # 解析多账户分隔符
    accounts_str_list = [env_value]
    for sep in ENV_CONFIG["separators"]:
        if sep in env_value:
            accounts_str_list = [s.strip() for s in env_value.split(sep) if s.strip()]
            break
    
    # 解析每个账户信息
    accounts = []
    for idx, account_str in enumerate(accounts_str_list, 1):
        parts = account_str.split("#", 2)
        
        # 格式校验（忽略推送链接部分）
        if len(parts) < 2:
            print(f"⚠️ 跳过格式错误账户{idx}：{account_str}（需为 账号#密码 格式）")
            continue
            
        acc, pwd = parts[0].strip(), parts[1].strip()
        
        if acc and pwd:
            accounts.append(AccountInfo(
                index=idx,
                account=acc,
                password=pwd
            ))
    
    if not accounts:
        raise ValueError("❌ 未加载到有效账户！请检查环境变量配置。")
    
    return accounts

# -------------------------- 核心业务逻辑 --------------------------
@retry_on_failure(max_retries=REQUEST_CONFIG["retry_times"])
def login_account(session: requests.Session, account: str, password: str) -> str:
    """账户登录，返回Token"""
    login_headers = get_base_headers()
    login_headers["Authorization"] = "Bearer null"
    
    encrypted_account = encrypt_account(account, password)
    login_data = {"account": encrypted_account, "source": "ipzan-home-one"}
    
    response = session.post(
        url=CONFIG_URLS["login"],
        headers=login_headers,
        json=login_data,
        timeout=REQUEST_CONFIG["timeout"]
    )
    response.raise_for_status()
    login_result = response.json()
    
    if login_result.get("code") != 0:
        raise ValueError(f"登录失败：{login_result.get('message', '未知错误')}")
    
    token = login_result.get("data", {}).get("token")
    if not token:
        raise ValueError("登录成功但未返回Token")
    
    return token

@retry_on_failure(max_retries=REQUEST_CONFIG["retry_times"])
def receive_ip(session: requests.Session, token: str) -> Dict[str, Any]:
    """领取IP，返回领取结果"""
    receive_headers = get_base_headers()
    receive_headers["Authorization"] = f"Bearer {token}"
    
    response = session.get(
        url=CONFIG_URLS["receive"],
        headers=receive_headers,
        timeout=REQUEST_CONFIG["timeout"]
    )
    response.raise_for_status()
    return response.json()

def process_single_account(account_info: AccountInfo) -> ProcessResult:
    """处理单个账户的完整流程"""
    account_masked = mask_account(account_info.account)
    print(f"\n[{account_info.index}] 📱 开始处理账号：{account_masked}")
    
    try:
        with request_session() as session:
            # 1. 登录
            token = login_account(session, account_info.account, account_info.password)
            print("  └─ ✅ 登录成功")
            
            # 2. 领取IP
            receive_result = receive_ip(session, token)
            code = receive_result.get("code")
            msg = receive_result.get("message", "")
            data = receive_result.get("data", "")
            
            # 3. 处理领取结果
            if code == 0:
                status = "success"
                message = f"领取成功：{data}"
                print(f"  └─ 🎉 {message}")
                
            elif code == -1 and "领取过" in str(msg):
                status = "duplicate"
                message = f"本周已领：{msg}"
                print(f"  └─ ⚠️ {message}")
                
            else:
                status = "failed"
                message = f"领取失败：{msg}"
                print(f"  └─ ❌ {message}")
            
            return ProcessResult(
                account_index=account_info.index,
                account_masked=account_masked,
                status=status,
                message=message,
                raw_data=receive_result
            )
            
    except Exception as e:
        error_msg = f"运行异常：{str(e)[:50]}"
        print(f"  └─ ❌ {error_msg}")
        
        return ProcessResult(
            account_index=account_info.index,
            account_masked=account_masked,
            status="error",
            message=error_msg
        )

# -------------------------- 主程序 --------------------------
def main():
    """主程序入口"""
    print("="*60)
    print("🎯 IPZAN 多账户自动领取工具（每周领IP）- 无推送版")
    print(f"🔗 注册链接：{CONFIG_URLS['home']}")
    print("="*60)
    
    all_summaries = []
    
    try:
        # 1. 加载账户
        accounts = load_accounts_from_env()
        print(f"\n📊 共加载 {len(accounts)} 个有效账户，开始执行任务...")
        
        # 2. 处理每个账户
        for idx, account in enumerate(accounts):
            result = process_single_account(account)
            
            # 构建汇总信息
            status_icon = {
                "success": "✅",
                "failed": "❌",
                "duplicate": "⚠️",
                "error": "❌"
            }.get(result.status, "❓")
            
            summary = f"账号{result.account_index}：{result.account_masked}\n{status_icon} {result.message}"
            all_summaries.append(summary)
            
            # 多账户延迟
            if idx < len(accounts) - 1:
                sleep_time = random.uniform(*REQUEST_CONFIG["sleep_range"])
                print(f"\n⏳ 多账户防并发，延迟 {sleep_time:.1f} 秒...")
                time.sleep(sleep_time)
                
    except Exception as e:
        error_summary = f"❌ 程序全局错误：{str(e)[:100]}"
        print(f"\n{error_summary}")
        all_summaries.append(error_summary)
        
    finally:
        # 输出最终结果
        print("\n" + "="*60)
        print("\n📝 执行结果汇总：")
        for summary in all_summaries:
            print(f"  {summary}")
        
        print("\n✅ 脚本执行完成！")
        print("="*60)

if __name__ == "__main__":
    main()

#!/usr/bin/python3
# -- coding: utf-8 -- 
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/only_for_happly
# @Time : 2025/06/14 14:23
# -------------------------------
# cron "15 20 6,15 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('小米运动')
#zepplife（原小米运动）注册后绑定支付宝微信同步步数
#变量为MI_USERS 格式如下 
# [
#   {
#     "phone": "手机号1",
#     "password": "密码1",
#     "min_step": 30000,
#     "max_step": 50000
#   },
#   {
#     "phone": "手机号2",
#     "password": "密码2",
#     "min_step": 20000,
#     "max_step": 22000
#   }
# ]  
# -*- coding: utf-8 -*-
import os
import json
import random
import time
import logging
import hmac
import hashlib
import base64
from datetime import datetime
from urllib.parse import urlencode, unquote, quote_plus
from functools import wraps

# --- 导入 requests 库，如果不存在则提示安装 ---
try:
    import requests
except ImportError:
    print("错误: 'requests' 库未安装。请运行 'pip install requests' 进行安装。")
    exit(1)

# --- 日志配置 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- 全局常量 ---
MAX_RETRIES = 3
RETRY_DELAY = 2  # 初始延迟时间（秒）
RETRY_MULTIPLIER = 1.5  # 延迟时间乘数


# --- 重试装饰器 ---
def with_retry(operation_name="请求"):
    """
    一个装饰器，为函数添加重试逻辑。
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = RETRY_DELAY
            for i in range(MAX_RETRIES):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.warning(f"{operation_name}失败: {e}。将在 {int(delay)} 秒后重试 ({i + 1}/{MAX_RETRIES})...")
                    if i < MAX_RETRIES - 1:
                        time.sleep(delay)
                        delay *= RETRY_MULTIPLIER
                    else:
                        logging.error(f"{operation_name}失败，已达到最大重试次数。")
                        raise  # 重新抛出最终的异常

        return wrapper

    return decorator


# --- 通知模块 ---
class Notifier:
    """
    处理所有通知服务的类。
    """

    def __init__(self):
        self.serverchan_key = os.getenv("SERVERCHAN_KEY")
        self.pushplus_token = os.getenv("PUSHPLUS_TOKEN")
        self.bark_key = os.getenv("BARK_KEY")
        self.tg_bot_token = os.getenv("TG_BOT_TOKEN")
        self.tg_chat_id = os.getenv("TG_CHAT_ID")
        self.dingtalk_webhook = os.getenv("DINGTALK_WEBHOOK")
        self.dingtalk_secret = os.getenv("DINGTALK_SECRET")
        self.wecom_key = os.getenv("WECOM_KEY")

    def send(self, title, content):
        """
        发送通知到所有已配置的平台。
        """
        logging.info("准备发送通知...")
        if self.serverchan_key:
            self._send_serverchan(title, content)
        if self.pushplus_token:
            self._send_pushplus(title, content)
        if self.bark_key:
            self._send_bark(title, content)
        if self.tg_bot_token and self.tg_chat_id:
            self._send_telegram(title, content)
        if self.dingtalk_webhook:
            self._send_dingtalk(title, content)
        if self.wecom_key:
            self._send_wecom(title, content)

    def _safe_request(self, method, url, platform, **kwargs):
        try:
            response = requests.request(method, url, timeout=10, **kwargs)
            if response.status_code == 200:
                logging.info(f"✅ {platform} 通知发送成功。响应: {response.text}")
            else:
                logging.error(f"❌ {platform} 通知发送失败。状态码: {response.status_code}, 响应: {response.text}")
        except Exception as e:
            logging.error(f"❌ 发送 {platform} 通知时出错: {e}")

    def _send_serverchan(self, title, content):
        url = f"https://sctapi.ftqq.com/{self.serverchan_key}.send"
        data = {"title": title, "desp": content}
        self._safe_request("POST", url, "Server酱", data=data)

    def _send_pushplus(self, title, content):
        url = "http://www.pushplus.plus/send"
        data = {"token": self.pushplus_token, "title": title, "content": content, "template": "markdown"}
        self._safe_request("POST", url, "PushPlus", json=data)

    def _send_bark(self, title, content):
        if self.bark_key.startswith("http"):
            url = f"{self.bark_key}/{quote_plus(title)}/{quote_plus(content)}"
        else:
            url = f"https://api.day.app/{self.bark_key}/{quote_plus(title)}/{quote_plus(content)}"
        self._safe_request("GET", url, "Bark")

    def _send_telegram(self, title, content):
        url = f"https://api.telegram.org/bot{self.tg_bot_token}/sendMessage"
        data = {"chat_id": self.tg_chat_id, "text": f"*{title}*\n\n{content}", "parse_mode": "Markdown"}
        self._safe_request("POST", url, "Telegram", data=data)

    def _send_dingtalk(self, title, content):
        url = self.dingtalk_webhook
        if self.dingtalk_secret:
            timestamp = str(round(time.time() * 1000))
            secret_enc = self.dingtalk_secret.encode('utf-8')
            string_to_sign = f'{timestamp}\n{self.dingtalk_secret}'
            hmac_code = hmac.new(secret_enc, string_to_sign.encode('utf-8'), digestmod=hashlib.sha256).digest()
            sign = quote_plus(base64.b64encode(hmac_code))
            url = f"{url}&timestamp={timestamp}&sign={sign}"

        data = {
            "msgtype": "markdown",
            "markdown": {"title": title, "text": f"## {title}\n\n{content}"}
        }
        self._safe_request("POST", url, "钉钉", json=data)

    # def _send_wecom(self, title, content):
    #     url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={self.wecom_key}"
    #     data = {
    #         "msgtype": "markdown",
    #         "markdown": {"content": f"## {title}\n\n{content.replace('\n', '\n\n')}"}
    #     }
    #     self._safe_request("POST", url, "企业微信", json=data)


# --- 核心业务逻辑 ---
class MiFit:
    """
    封装与小米运动 API 交互的核心逻辑。
    """

    def __init__(self, user_config, data_template):
        self.phone = user_config["phone"]
        self.password = user_config["password"]
        self.min_step = user_config.get("min_step", 18000)
        self.max_step = user_config.get("max_step", 25000)
        self.data_template = data_template
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MiFit/4.6.0 (iPhone; iOS 14.0.1; Scale/2.00)'
        })
        self.user_id = None
        self.app_token = None

    @with_retry("获取登录 Code")
    def _get_code(self):
        """第一步：使用手机号和密码登录，获取重定向URL中的 access code。"""
        url = f"https://api-user.huami.com/registrations/+86{self.phone}/tokens"
        data = {
            "client_id": "HuaMi",
            "password": self.password,
            "redirect_uri": "https://s3-us-west-2.amazonaws.com/hm-registration/successsignin.html",
            "token": "access",
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}

        response = self.session.post(
            url, data=urlencode(data), headers=headers, allow_redirects=False
        )
        response.raise_for_status()  # 确保请求成功

        location = response.headers.get("Location")
        if not location or "access=" not in location:
            raise Exception("获取登录 Code 失败，响应中未找到 Location 或 access code。")

        code = location.split("access=")[1].split("&")[0]
        logging.info(f"✅ 账号 {self.phone[-4:]}: 获取登录 Code 成功。")
        return code

    @with_retry("获取 Login Token")
    def _get_login_token(self, code):
        """第二步：使用 code 换取 login_token 和 user_id。"""
        url = "https://account.huami.com/v2/client/login"
        data = {
            "app_name": "com.xiaomi.hm.health",
            "app_version": "4.6.0",
            "code": code,
            "country_code": "CN",
            "device_id": "2C8B4939-0CCD-4E94-8CBA-CB8EA6E613A1",
            "device_model": "phone",
            "grant_type": "access_token",
            "third_name": "huami_phone",
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}

        response = self.session.post(url, data=urlencode(data), headers=headers)
        response_json = response.json()

        if "token_info" not in response_json:
            raise Exception(f"获取 Login Token 失败: {response_json.get('message', '未知错误')}")

        self.user_id = response_json["token_info"]["user_id"]
        login_token = response_json["token_info"]["login_token"]
        logging.info(f"✅ 账号 {self.phone[-4:]}: 获取 Login Token 和 UserID 成功。")
        return login_token

    @with_retry("获取 App Token")
    def _get_app_token(self, login_token):
        """第三步：使用 login_token 换取 app_token，这是与数据API交互的最终凭证。"""
        url = "https://account.huami.com/v1/client/app_tokens"
        params = {
            "app_name": "com.xiaomi.hm.health",
            "dn": "api-user.huami.com,api-mifit.huami.com,app-analytics.huami.com",
            "login_token": login_token,
        }

        response = self.session.get(url, params=params)
        response_json = response.json()

        if "token_info" not in response_json:
            raise Exception(f"获取 App Token 失败: {response_json.get('message', '未知错误')}")

        self.app_token = response_json["token_info"]["app_token"]
        logging.info(f"✅ 账号 {self.phone[-4:]}: 获取 App Token 成功。")

    def _process_data(self, step):
        """
        处理数据模板，更新日期和步数。
        这是一个更稳健的实现，通过解析JSON来修改。
        """
        logging.info("📦 正在处理数据模板...")
        # 1. URL解码
        decoded_template = unquote(self.data_template)
        # 2. 解析为Python对象 (List)
        data_list = json.loads(decoded_template)

        # 3. 修改日期
        today_str = datetime.now().strftime("%Y-%m-%d")
        data_list[0]['date'] = today_str
        logging.info(f"📅 日期已更新为: {today_str}")

        # 4. 修改步数
        # `summary` 是一个字符串形式的JSON，需要再次解析
        summary_dict = json.loads(data_list[0]['summary'])
        summary_dict['stp']['ttl'] = step
        logging.info(f"👣 步数已更新为: {step}")

        # 5. 将修改后的 summary 写回
        # 使用 separators 去除空格，使其与原始格式更接近
        data_list[0]['summary'] = json.dumps(summary_dict, separators=(',', ':'))

        # 6. 将整个对象转回为JSON字符串
        return json.dumps(data_list)

    @with_retry("发送步数数据")
    def _send_data(self, data_json):
        """第四步：将处理好的数据发送到服务器。"""
        url = "https://api-mifit-cn2.huami.com/v1/data/band_data.json"
        data = {
            "userid": self.user_id,
            "last_sync_data_time": "1597306380",
            "device_type": "0",
            "last_deviceid": "DA932FFFFE8816E7",
            "data_json": data_json,
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'apptoken': self.app_token,
        }

        response = self.session.post(url, data=urlencode(data), headers=headers)
        response_json = response.json()

        if response_json.get("message") == "success":
            logging.info(f"✅ 账号 {self.phone[-4:]}: 数据发送成功！服务器响应: {response_json}")
        else:
            raise Exception(f"数据发送失败，服务器响应: {response_json}")

    def run(self):
        """
        执行修改步数的完整流程。
        """
        # 随机生成步数
        if self.max_step < self.min_step:
            self.min_step, self.max_step = self.max_step, self.min_step

        target_step = random.randint(self.min_step, self.max_step)
        logging.info(f"--- 正在为账号 {self.phone[-4:]} 执行任务，目标步数: {target_step} ---")

        # 1. 获取 Code
        code = self._get_code()

        # 2. 获取 Token
        login_token = self._get_login_token(code)

        # 3. 获取 App Token
        self._get_app_token(login_token)

        # 4. 处理数据
        processed_json = self._process_data(target_step)

        # 5. 发送数据
        self._send_data(processed_json)

        logging.info(f"🎉 账号 {self.phone[-4:]} 任务成功完成！")
        return f"账号 {self.phone[-4:]} 成功: 步数修改为 {target_step}"


# --- 主函数 ---
def main():
    """
    主执行函数，负责读取配置并为每个用户运行任务。
    """
    users_json = os.getenv("MI_USERS")
    data_json_template = os.getenv("MI_DATA_JSON")

    if not users_json or not data_json_template:
        logging.error("❌ 环境变量 'MI_USERS' 或 'MI_DATA_JSON' 未设置，脚本无法运行。")
        return

    try:
        users = json.loads(users_json)
        if not isinstance(users, list) or not users:
            raise ValueError("MI_USERS 格式错误，应为一个非空的JSON数组。")
    except (json.JSONDecodeError, ValueError) as e:
        logging.error(f"❌ 解析 MI_USERS 环境变量失败: {e}")
        return

    notifier = Notifier()
    success_count = 0
    failure_count = 0

    logging.info(f"共找到 {len(users)} 个账户，开始执行任务...")

    for i, user_config in enumerate(users):
        start_time = time.time()
        try:
            if "phone" not in user_config or "password" not in user_config:
                logging.error(f"第 {i + 1} 个用户配置缺少 'phone' 或 'password'，已跳过。")
                failure_count += 1
                continue

            mifit_runner = MiFit(user_config, data_json_template)
            result_message = mifit_runner.run()
            success_count += 1
        except Exception as e:
            failure_count += 1
            phone = user_config.get("phone", "未知")
            error_message = f"❌ 账号 {phone[-4:]} 任务失败: {e}"
            logging.error(error_message)
            # 发送失败通知
            notifier.send(
                title="小米运动步数修改失败通知",
                content=error_message
            )
        finally:
            end_time = time.time()
            logging.info(f"账号 {user_config.get('phone', '未知')[-4:]} 本次任务耗时: {end_time - start_time:.2f} 秒\n")

    logging.info("=" * 40)
    logging.info(f"所有任务执行完毕。成功: {success_count}, 失败: {failure_count}")
    logging.info("=" * 40)


if __name__ == "__main__":
    main()



#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/just_for_happy
# @Time : 2025/7/22 13:23
# -------------------------------
# cron "30 5 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('联想乐豆任务')

import os
import time
import random
import json
import re
import hashlib
from datetime import datetime
import asyncio
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64

# 每日做联想乐豆任务 可以换东西
# 变量名lenovoAccessToken 请求头Headers 中 accesstoken 的值 多账号&或换行 分割 或新建同名变量
class JSEncrypt:
    def __init__(self):
        self.public_key = None

    def setPublicKey(self, key):
        try:
            decoded_key = base64.b64decode(key.encode())
            self.public_key = RSA.import_key(decoded_key)
        except Exception as e:
            print(f"Error setting public key: {e}")
            try:
                pem_key = f"-----BEGIN PUBLIC KEY-----\n{key}\n-----END PUBLIC KEY-----"
                self.public_key = RSA.import_key(pem_key)
            except Exception as e_pem:
                print(f"Error setting public key as PEM: {e_pem}")
                self.public_key = None

    def encrypt(self, text):
        if not self.public_key:
            print("Error: Public key not set for encryption.")
            return None
        try:
            cipher_rsa = PKCS1_v1_5.new(self.public_key)
            encrypted_data = cipher_rsa.encrypt(text.encode("utf-8"))
            return base64.b64encode(encrypted_data).decode("utf-8")
        except Exception as e:
            print(f"Error during RSA encryption: {e}")
            return None

class Env:
    def __init__(self, t, s=None):
        self.name = t
        self.logs = []
        self.logSeparator = "\n"
        self.startTime = time.time() * 1000  # Convert to milliseconds
        if s:
            for key, value in s.items():
                setattr(self, key, value)
        self.log("", f"\U0001f514{self.name},\u5f00\u59cb!")

    def isNode(self):
        return True

    def isQuanX(self):
        return False

    def queryStr(self, options):
        return "&".join([f"{key}={json.dumps(value) if isinstance(value, (dict, list)) else value}" for key, value in options.items()])

    def getURLParams(self, url):
        params = {}
        if "?" in url:
            queryString = url.split("?")[1]
            if queryString:
                paramPairs = queryString.split("&")
                for pair in paramPairs:
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        params[key] = value
        return params

    def isJSONString(self, s):
        try:
            return isinstance(json.loads(s), (dict, list))
        except (json.JSONDecodeError, TypeError):
            return False

    def isJson(self, obj):
        return isinstance(obj, dict)

    async def sendMsg(self, message):
        if not message: return
        print(f"[Notification] {message}")

    def randomNumber(self, length):
        characters = "0123456789"
        return "".join(random.choice(characters) for _ in range(length))

    def randomString(self, length):
        characters = "abcdefghijklmnopqrstuvwxyz0123456789"
        return "".join(random.choice(characters) for _ in range(length))

    def timeStamp(self):
        return int(time.time() * 1000)

    def uuid(self):
        import uuid
        return str(uuid.uuid4())

    def time(self, t_format):
        now = datetime.now()
        replacements = {
            "M+": now.month,
            "d+": now.day,
            "H+": now.hour,
            "m+": now.minute,
            "s+": now.second,
            "q+": (now.month - 1) // 3 + 1,
            "S": now.microsecond // 1000,
        }
        t_format = re.sub(r"(y+)", lambda m: str(now.year)[4 - len(m.group(1)):], t_format)
        for key, value in replacements.items():
            t_format = re.sub(f"({key})", lambda m: f"{value:0{len(m.group(1))}}" if len(m.group(1)) > 1 else str(value), t_format)
        return t_format

    def msg(self, title, subtitle="", body="", options=None):
        logs = ["", "==============📣系统通知📣=============="]
        logs.append(title)
        if subtitle: logs.append(subtitle)
        if body: logs.append(body)
        print("\n".join(logs))
        self.logs.extend(logs)

    def log(self, *args):
        if args:
            self.logs.extend(args)
            print(self.logSeparator.join(map(str, args)))

    def logErr(self, t, s):
        print(f"\U00002757\U0000fe0f{self.name},\u9519\u8bef!", t)
        if hasattr(t, "stack"):
            print(t.stack)

    async def wait(self, t):
        await asyncio.sleep(t / 1000)

    def done(self, t={}):
        s = time.time() * 1000
        e = (s - self.startTime) / 1000
        self.log("", f"\U0001f514{self.name},\u7ed3\u675f!\U0001f55b {e}\u79d2")
        self.log()
        print("Script finished.")

_env = Env("联想App")

ckName = "lenovoAccessToken"
envSplitor = ["&", "\n"]
strSplitor = "#"
userIdx = 0
userList = []

class Task:
    def __init__(self, s):
        global userIdx
        userIdx += 1
        self.index = userIdx
        self.ck = None
        self.ckStatus = True
        self.token = None
        self.accesstoken = s.split(strSplitor)[0]

    async def main(self):
        await self.ssoCheck()
        print(self.ck, self.token)
        if self.ck and self.token:
            await self.userInfo()
            await self.checkIn()
            await self.getUserTaskList()
            await self.wait(3, 10)

    async def userInfo(self):
        result = await self.taskRequest(method="POST", url="https://mmembership.lenovo.com.cn/member-hp-webapi/v1/userBenefit/getMyAssets")
        if result and result.get("code") == "0":
            _env.log(f"✅账号[{self.index}] 获取用户信息成功===>[[{result['data']['userId']}]]乐豆[[{result['data']['ledouNum']}]]")
            self.ckStatus = True
        else:
            _env.log(f"❌账号[{self.index}] 获取用户状态失败")
            print(result)
            self.ckStatus = False

    async def isSignIn(self):
        result = await self.taskRequest(method="POST", url=f"https://mmembership.lenovo.com.cn/member-hp-task-center/v1/task/getCheckInList?lenovoId={self.ck}")
        if result and result.get("code") == "0":
            if result["data"]["flag"] == False:
                _env.log(f"✅账号[{self.index}] 今日未签到 =====> 签到ing🎉")
                await self.checkIn()
        else:
            _env.log(f"❌账号[{self.index}] 获取签到状态")
            print(result)

    async def checkIn(self):
        result = await self.taskRequest(method="POST", url=f"https://mmembership.lenovo.com.cn/member-hp-task-center/v1/task/checkIn?lenovoId={self.ck}&OSType=10011")
        if result and result.get("code") == "0":
            _env.log(f"✅账号[{self.index}] 签到成功🎉")
        else:
            _env.log(f"❌账号[{self.index}] 签到失败")
            print(result)

    def getSignKey(self):
        jsencrypt_instance = JSEncrypt()
        pt = ["cD", "BT", "Uzn", "Po", "Luu", "Yhc", "Cj", "FP", "al", "Tq"]
        ht = ["MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJB", "L7qpP6mG6ZHdDKEIdTqQDo/WQ", "6NaWftXwOTHnnbnwUEX2/2jI4qALxRWMliYI80cszh6", "ySbap0KIljDCN", "w0CAwEAAQ=="]

        def mt(text):
            n = ""
            try:
                e = ""
                for i, val in enumerate(ht):
                    e += val + (["A", "b", "C", "D", ""])[i] if i < len(["A", "b", "C", "D", ""]) else val
                jsencrypt_instance.setPublicKey(e)
                n = jsencrypt_instance.encrypt(text)
            except Exception as t_err:
                print("rsa加密错误！", n, t_err)
            return n

        def generate_random_number_string(length=8):
            return str(random.randint(0, 10**length - 1)).zfill(length)

        t = generate_random_number_string(8)
        e = ""
        for char_digit in t:
            e += pt[int(char_digit)]
        return mt(f"{t}:{e}")

    async def getUserTaskList(self):
        result = await self.taskRequest(method="POST", url="https://mmembership.lenovo.com.cn/member-hp-task-center/v1/task/getUserTaskList")
        if result and result.get("code") == "0":
            _env.log(f"✅账号[{self.index}] 获取任务列表成功🎉")
            for task in result["data"]:
                if task["taskState"] == 0 and task["type"] != 13:
                    await _env.wait(5000)
                    await self.doTask(task["taskId"])
        else:
            _env.log(f"❌账号[{self.index}] 获取任务列表失败")
            print(result)

    async def doTask(self, task_id):
        result_ = await self.taskRequest(method="POST", url=f"https://mmembership.lenovo.com.cn/member-hp-task-center/v1/checkin/selectTaskPrize?taskId={task_id}&channelId=1")
        if result_ and result_.get("code") == "0":
            result = await self.taskRequest(method="POST", url=f"https://mmembership.lenovo.com.cn/member-hp-task-center/v1/Task/userFinishTask?taskId={task_id}&channelId=1&state=1")
            if result and result.get("code") == "0":
                _env.log(f"✅账号[{self.index}] 任务执行成功🎉")
            else:
                _env.log(f"❌账号[{self.index}] 任务执行失败")
                print(result_.get("message"))
                print(task_id)
        else:
            print(result_.get("message"))

    async def ssoCheck(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Lite Build/QKQ1.190910.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.99 Mobile Safari/537.36/lenovoofficialapp/9e4bb0e5bc326fb1_10219183246/newversion/versioncode-1000112/",
            "Accept-Encoding": "gzip, deflate",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "accesstoken": self.accesstoken,
            "signkey": self.getSignKey(),
            "origin": "https://mmembership.lenovo.com.cn",
            "servicetoken": "",
            "tenantid": "25",
            "sec-fetch-dest": "empty",
            "clientid": "2",
            "x-requested-with": "com.lenovo.club.app",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "referer": "https://mmembership.lenovo.com.cn/app?pmf_source=P0000005611M0002",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        config = {
            "method": "POST",
            "url": "https://mmembership.lenovo.com.cn/member-center-api/v2/access/ssoCheck?lenovoId=&unionId=&clientId=2",
            "headers": headers
        }
        try:
            response = requests.request(**config)
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            result = None

        if result and result.get("code") == "0":
            self.token = result["data"]["serviceToken"]
            self.ck = result["data"]["lenovoId"]
        else:
            print(f"ssoCheck failed: {result}")

    async def taskRequest(self, method, url, data=None):
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Lite Build/QKQ1.190910.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.99 Mobile Safari/537.36/lenovoofficialapp/9e4bb0e5bc326fb1_10219183246/newversion/versioncode-1000112/",
            "Accept-Encoding": "gzip, deflate",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "origin": "https://mmembership.lenovo.com.cn",
            "servicetoken": self.token,
            "lenovoid": self.ck,
            "clientid": "2",
            "x-requested-with": "com.lenovo.club.app",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "referer": "https://mmembership.lenovo.com.cn/app?pmf_source=P0000005611M0002",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        config = {
            "method": method,
            "url": url,
            "headers": headers,
            "json": data if method.upper() == "POST" else None
        }
        try:
            response = requests.request(**config)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Task request failed: {e}")
            return None

    async def wait(self, min_second, max_second):
        random_second = random.uniform(min_second, max_second)
        print(f"等候 {min_second}-{max_second}({random_second}) 秒")
        await asyncio.sleep(random_second)

async def checkEnv():
    userCookie = os.environ.get(ckName)
    if not userCookie:
        print(f"未找到CK【{ckName}】")
        return False

    e = envSplitor[0]
    for o in envSplitor:
        if o in userCookie:
            e = o
            break

    for n in userCookie.split(e):
        if n:
            userList.append(Task(n))

    print(f"共找到{len(userList)}个账号")
    return True

async def main():
    print("==================================================\n 脚本执行 - 北京时间(UTC+8): {} \n==================================================".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    if not await checkEnv():
        return

    if len(userList) > 0:
        for user in userList:
            if user.ckStatus:
                await user.main()

    await _env.sendMsg("\n".join(_env.logs))

if __name__ == "__main__":
    asyncio.run(main())

import requests
import json
import time
import re
import os  # 导入 os 库以读取环境变量

# 浙江数字工会小程序 首页banner 查看详情---点点抽大奖
# ================= 变量获取区域 (适配青龙) =================
# 1. DeepSeek 配置：在青龙环境变量添加 DEEPSEEK_API_KEY
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# 2. 账号列表：在青龙环境变量添加 ZJSZGH_TOKEN，多账号用换行或 & 分隔
# 例子：4198db...&c6cb78...
raw_accounts = os.getenv("ZJSZGH_TOKEN", "")
if "&" in raw_accounts:
    ACCOUNTS = raw_accounts.split("&")
elif "\n" in raw_accounts:
    ACCOUNTS = raw_accounts.split("\n")
else:
    ACCOUNTS = [raw_accounts] if raw_accounts else []

# 3. 推送配置：在青龙环境变量添加 PUSH_PLUS_TOKEN
PUSH_PLUS_TOKEN = os.getenv("PUSH_PLUS_TOKEN", "")

# 4. 运行延迟设置 (也可以设为环境变量，这里给默认值)
SLEEP_BETWEEN_TASKS = int(os.getenv("SLEEP_TASKS", "2"))
SLEEP_BETWEEN_ACCOUNTS = int(os.getenv("SLEEP_ACCOUNTS", "5"))
# =========================================================

BASE_URL = "https://zjszgh.org.cn/szgh_s2/grassroots-workbench/api/app/themed/raffle/activity"


def Push(contents, title='中奖提醒'):
    """PushPlus 推送函数"""
    if not PUSH_PLUS_TOKEN: return
    try:
        payload = {
            "token": PUSH_PLUS_TOKEN,
            "title": title,
            "content": contents.replace('\n', '<br>'),
            "template": "html"
        }
        requests.post('http://www.pushplus.plus/send', json=payload, timeout=10)
    except Exception as e:
        print(f"    ⚠️ 推送出错: {e}")


def get_headers(token):
    return {
        "Host": "zjszgh.org.cn",
        "Authorization": token.strip(),  # 去除可能存在的空格
        "Content-Type": "application/json",
        "SZ-CHANNEL": "0",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "Referer": "https://zjszgh.org.cn/webapp/toolkitMobile/index.html"
    }


def ask_deepseek(question_text, options):
    """请求 AI 获取答案"""
    if not DEEPSEEK_API_KEY:
        print("❌ 未配置 DEEPSEEK_API_KEY，默认选 A")
        return "A"
    prompt = f"你是一个猜灯谜专家。请从以下选项中选出唯一正确答案，仅回复选项字母：\n题目：{question_text}\n选项：{options}"
    try:
        response = requests.post("https://api.deepseek.com/chat/completions", json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }, headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}, timeout=15)

        if response.status_code != 200:
            return "A"

        res = response.json()
        content = res['choices'][0].get('message', {}).get('content', '')
        match = re.search(r'[A-D]', content.strip().upper())
        return match.group() if match else "A"
    except:
        return "A"


def run_tasks_for_account(token, index):
    headers = get_headers(token)
    print(f"\n🚀 【账号 {index + 1}】 开始执行任务...")

    # --- 1. 祈福任务 ---
    print("🌳 正在祈福...", end=" ", flush=True)
    try:
        res = requests.get(f"{BASE_URL}/finishPrayTree", headers=headers, timeout=10).json()
        print(f"结果: {res.get('msg', '未知响应')}")
    except Exception as e:
        print(f"异常: {e}")

    time.sleep(SLEEP_BETWEEN_TASKS)

    # --- 2. 答题任务 ---
    print("🎁 正在答题...", end=" ", flush=True)
    try:
        res_get = requests.get(f"{BASE_URL}/making/riddle/papers", headers=headers, timeout=10).json()
        if res_get.get("code") == 200:
            paper_data = res_get["data"]
            submit_answers = []
            for q in paper_data["questionList"]:
                opts = " | ".join([f"{o['option']}.{o['content']}" for o in q["options"]])
                answer = ask_deepseek(q["content"], opts)
                submit_answers.append({"questionId": q["questionId"], "answerList": [answer]})

            res_post = requests.post(f"{BASE_URL}/submit/riddle/papers", headers=headers,
                                     json={"papersId": paper_data["papersId"], "answerList": submit_answers},
                                     timeout=10).json()
            right_num = res_post.get('data', {}).get('rightNum', 0)
            print(f"完成！答对数: {right_num}")
        else:
            print(f"跳过: {res_get.get('msg')}")
    except Exception as e:
        print(f"异常: {e}")

    time.sleep(SLEEP_BETWEEN_TASKS)

    # --- 3. 抽奖任务 ---
    print("🎁 正在抽奖...", end=" ", flush=True)
    try:
        res = requests.get(f"{BASE_URL}/execute/raffle?actId=1", headers=headers, timeout=10).json()
        if res.get("code") == 200:
            result = res.get("data", {})
            if result.get("hitFlag") == 1:
                prize = result.get('prizeInfo')
                print(f"🎉 刚刚中奖了: {prize}")
                Push(f"账号[{index + 1}] 实时中奖: {prize}", title="🎊 浙工之家抽奖中奖")
            else:
                print("📉 未中奖")
        else:
            print(f"失败: {res.get('msg')}")
    except Exception as e:
        print(f"异常: {e}")

    time.sleep(SLEEP_BETWEEN_TASKS)

    # --- 4. 查询历史中奖记录 ---
    print("🔍 正在查询中奖记录...", end=" ", flush=True)
    try:
        record_url = f"{BASE_URL}/user/raffle/prize/page/list?pageNo=1&pageSize=20"
        res = requests.get(record_url, headers=headers, timeout=10).json()
        if res.get("code") == 200:
            prizes = res.get("data", {}).get("resultList", [])
            if not prizes:
                print("暂无记录")
            else:
                print(f"共发现 {len(prizes)} 个奖品")
                for p in prizes:
                    name = p.get('prizeName')
                    code = p.get('code', '无券码')
                    expire = p.get('expire', '无日期')
                    print(f"    📜 {name} | 券码: {code} | 有效期: {expire}")
        else:
            print(f"查询失败: {res.get('msg')}")
    except Exception as e:
        print(f"查询异常: {e}")


if __name__ == "__main__":
    if not ACCOUNTS:
        print("❌ 错误：未在环境变量中检测到 ZJSZGH_TOKEN")
    else:
        print(f"--- 脚本启动 (检测到账号数: {len(ACCOUNTS)}) ---")
        for i, token in enumerate(ACCOUNTS):
            if not token.strip(): continue
            run_tasks_for_account(token, i)
            if i < len(ACCOUNTS) - 1:
                print(f"等待 {SLEEP_BETWEEN_ACCOUNTS} 秒后切换账号...")
                time.sleep(SLEEP_BETWEEN_ACCOUNTS)
        print("\n✅ 所有任务已跑完。")
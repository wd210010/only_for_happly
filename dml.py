import os
import time
import requests
import json
import logging
from dotenv import load_dotenv
from notification import Push

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- Constants ---
GAME_DONE_URL = "https://game.dominos.com.cn/bulgogi/game/gameDone"
SHARING_DONE_URL = "https://game.dominos.com.cn/bulgogi/game/sharingDone"
API_SUCCESS_CODE = 0
DEFAULT_TEMP_ID = "16408240716151126162"
SHARE_FROM_VALUE = 1
SHARE_TARGET_VALUE = 0
MAX_SHARE_ATTEMPTS = 5 # 假设最多尝试分享5次
MAX_GAME_ATTEMPTS = 3 # 游戏尝试次数

def process_account(account_id, openid, headers):
    """处理单个达美乐账户的分享和抽奖逻辑"""
    account_message = []
    logging.info(f"\n=======达美乐开始执行账号{account_id}=======")

    # 分享逻辑
    share_success = False
    for attempt in range(1, MAX_SHARE_ATTEMPTS + 1):
        share_payload = f"openid={openid}&from={SHARE_FROM_VALUE}&target={SHARE_TARGET_VALUE}"
        try:
            res = requests.post(SHARING_DONE_URL, data=share_payload, headers=headers).json()
            error_message = res.get("errorMessage")
            if error_message == "今日分享已用完，请明日再来":
                logging.info(f"账号{account_id}分享已达上限，明天再来吧")
                share_success = True
                break
            elif res.get("statusCode") == API_SUCCESS_CODE:
                logging.info(f"账号{account_id}分享成功，第 {attempt} 次尝试。")
                # 如果有其他逻辑判断是否继续分享，可以在这里添加
                share_success = True # 假设成功一次即可
                break
            else:
                logging.warning(f"账号{account_id}分享失败: {error_message}")
                account_message.append(f"账号{account_id}分享失败: {error_message}")
                break # 分享失败，不再尝试
        except requests.exceptions.RequestException as e:
            logging.error(f"账号{account_id}分享API请求失败: {e}")
            account_message.append(f"账号{account_id}分享API请求失败: {e}")
            break
        except json.JSONDecodeError as e:
            logging.error(f"账号{account_id}分享JSON解析失败: {e}")
            account_message.append(f"账号{account_id}分享JSON解析失败: {e}")
            break
    if not share_success:
        logging.info(f"账号{account_id}未能完成分享或达到最大尝试次数。")
        account_message.append(f"账号{account_id}未能完成分享或达到最大尝试次数。")

    # 抽奖逻辑
    game_payload = f"openid={openid}&score=d8XtWSEx0zRy%2BxdeJriXZeoTek6ZVZdadlxdTFiN9yrxt%2BSIax0%2BRccbkObBZsisYFTquPg%2FG2cnGPBlGV2f32C6D5q3FFhgvcfJP9cKg%2BXs6l7J%2BEcahicPml%2BZWp3P4o1pOQvNdDUTQgtO6NGY0iijZ%2FLAmITy5EJU8dAc1EnbvhOYG36Qg1Ji4GDRoxAfRgmELvpLM6JSFlCEKG2C2s%2BJCevOJo7kwsLJCvwbVgeewhKSAyCZYnJQ4anmPgvrv6iUIiFQP%2Bj6%2B5p1VETe5xfawQ4FQ4w0mttXP0%2BhX39n1dzDrfcSkYkUaWPkIFlHAX7QPT3IgG6MhIKCvB%2BUcw%3D%3D&tempId={DEFAULT_TEMP_ID}"
    for attempt in range(1, MAX_GAME_ATTEMPTS + 1):
        try:
            response = requests.post(GAME_DONE_URL, data=game_payload, headers=headers)
            response.raise_for_status() # 检查HTTP状态码
            response_json = response.json()
            status_code = response_json.get("statusCode")

            if status_code == API_SUCCESS_CODE:
                prize = response_json.get("content", {}).get("name")
                if prize:
                    logging.info(f"账号{account_id} 第{attempt}次抽奖: {prize}")
                    account_message.append(f"第{attempt}次抽奖: {prize}")
                    if "一等奖" in prize:
                        Push(title="达美乐披萨中奖推送", contents=f"账号{account_id}\n{prize}")
                else:
                    logging.warning(f"账号{account_id} 第{attempt}次抽奖成功但未获取到奖品名称。")
                    account_message.append(f"第{attempt}次抽奖成功但未获取到奖品名称。")
                # 如果只需要一次成功，可以在这里添加 break
                # break
            else:
                err = response_json.get("errorMessage", "未知错误")
                logging.warning(f"账号{account_id} 第{attempt}次抽奖失败: {err}")
                account_message.append(f"第{attempt}次抽奖失败: {err}")
                break # 抽奖失败，不再尝试
        except requests.exceptions.RequestException as e:
            logging.error(f"账号{account_id} 第{attempt}次抽奖API请求失败: {e}")
            account_message.append(f"账号{account_id} 第{attempt}次抽奖API请求失败: {e}")
            break
        except json.JSONDecodeError as e:
            logging.error(f"账号{account_id} 第{attempt}次抽奖JSON解析失败: {e}")
            account_message.append(f"账号{account_id} 第{attempt}次抽奖JSON解析失败: {e}")
            break
        except KeyError as e:
            logging.error(f"账号{account_id} 第{attempt}次抽奖API响应缺少关键字段: {e}")
            account_message.append(f"账号{account_id} 第{attempt}次抽奖API响应缺少关键字段: {e}")
            break
    return "\n".join(account_message)

def main():
    load_dotenv()
    dominos_accounts_str = os.getenv("dmlck") # 保持环境变量名不变，但内部使用更清晰的变量名
    plustoken = os.getenv("plustoken") # 确保plustoken在main函数中被获取，以便Push函数使用

    if not dominos_accounts_str:
        logging.error("dmlck 环境变量未设置，退出。")
        return

    dominos_accounts_list = dominos_accounts_str.split("&")
    total_message = []

    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 12; M2012K11AC Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/122.0.6261.120 Mobile Safari/537.36 XWEB/1220133 MMWEBSDK/20240404 MMWEBID/8518 MicroMessenger/8.0.49.2600(0x2800313D) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
        'Accept-Encoding': "gzip,compress,br,deflate",
        'Content-Type': "application/x-www-form-urlencoded",
        'charset': "utf-8",
        'Referer': "https://servicewechat.com/wx887bf6ad752ca2f2/63/page-frame.html" # 注意这里Referer可能需要根据实际情况调整
    }

    for i, account_str in enumerate(dominos_accounts_list, start=1):
        account_parts = account_str.split(",")
        if not account_parts or not account_parts[0]:
            logging.warning(f"账号 {i} 格式不正确或为空，跳过。")
            total_message.append(f"账号 {i} 格式不正确或为空，跳过。")
            continue
        openid = account_parts[0]
        account_result = process_account(i, openid, headers)
        total_message.append(account_result)

    final_message = "\n".join(total_message)
    try:
        # 使用新的Push函数，确保plustoken已在环境变量中设置
        Push(title="达美乐", contents=final_message)
    except Exception as e:
        logging.error(f"推送失败: {e}")

if __name__ == "__main__":
    main()



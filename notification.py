import requests
import os

def Push(title, contents):
    plustoken = os.getenv("plustoken")
    if not plustoken:
        print("plustoken is not set, skipping push notification.")
        return
    headers = {"Content-Type": "application/json"}
    json_data = {"token": plustoken, "title": title, "content": contents.replace("\n", "<br>"), "template": "json"}
    try:
        resp = requests.post("http://www.pushplus.plus/send", json=json_data, headers=headers).json()
        print("push+推送成功" if resp["code"] == 200 else "push+推送失败")
    except requests.exceptions.RequestException as e:
        print(f"push+推送失败: {e}")



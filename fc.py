#!/usr/bin/python3
# -- coding: utf-8 --
# @Time : 2025/8/8 9:23
# -------------------------------
# cron "30 8 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('福彩活动');
# 活动地址:
# 变量名fcau  抓取https://ulxhh25-serv.cwlo.com.cn这个域名下的Authorization 如果填配置文件就用&隔开 或者一个个的加入环境变量

import requests
import json
import os
from typing import List, Dict, Any


class WelfareActivity:
    BASE_URL = 'https://ulxhh25-serv.cwlo.com.cn/api'

    def __init__(self, auth_token: str):
        self.headers = {
            "Authorization": auth_token,
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.47(0x18002f2c) NetType/WIFI Language/zh_CN",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _post(self, endpoint: str, data: Dict = None) -> Dict:
        """Helper method for POST requests with error handling"""
        try:
            response = self.session.post(f"{self.BASE_URL}/{endpoint}", data=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"请求失败: {endpoint} - {str(e)}")
            return {}

    def get_sun_list(self) -> List[Dict]:
        """获取阳光列表"""
        print('开始获取阳光列表>>')
        data = self._post('user/sun/list', data={'last_id': ''})
        return data.get('data', {}).get('list', [])

    def collect_sun(self, sun_id: str) -> Dict:
        """收获阳光"""
        print(f'开始获取阳光 {sun_id}>>')
        return self._post('user/sun/status', data={'id': sun_id})

    def get_flower_count(self) -> int:
        """获取花朵数"""
        print('开始获取花朵数>>')
        data = self._post('user/info')
        return data.get('data', {}).get('user', {}).get('flower', 0)

    def donate_flower(self) -> Dict:
        """赠送花朵"""
        print('开始赠送花朵>>')
        return self._post('welfare/donation', data={'project_id': 1})

    def get_lottery_count(self) -> int:
        """获取抽奖次数"""
        data = self._post('lottery/user')
        return data.get('data', {}).get('lottery_count', 0)

    def start_lottery(self) -> Dict:
        """执行抽奖"""
        return self._post('lottery/start')


def main():
    # 获取授权列表
    auth_tokens = os.getenv("fcau", "").split('&')
    print(f'获取到{len(auth_tokens)}个账号\n{"*" * 20}')

    for idx, token in enumerate(auth_tokens, 1):
        print(f'\n开始执行账号{idx}')
        try:
            activity = WelfareActivity(token)

            # 获取并处理阳光
            for sun in activity.get_sun_list():
                print(f"处理阳光ID: {sun['id']}")
                print(activity.collect_sun(sun['id']))

            # 处理花朵
            flower_count = activity.get_flower_count()
            print(f'当前剩余花朵: {flower_count}')
            if flower_count == 0:
                print('不执行赠花')
            else:
                for _ in range(flower_count):
                    print(activity.donate_flower())

            # 处理抽奖
            lottery_count = activity.get_lottery_count()
            print(f'剩余抽奖次数: {lottery_count}')
            if lottery_count == 0:
                print('不执行抽奖')
            else:
                for _ in range(lottery_count):
                    print(activity.start_lottery())

        except Exception as e:
            print(f'账号{idx}执行失败: {str(e)}')
            continue


if __name__ == '__main__':
    main()

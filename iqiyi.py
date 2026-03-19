import os
import re
import time
import json
import uuid
import requests
from datetime import datetime

# 爱奇艺全功能签到脚本 需要时vip才运行 变量 IQIYI_COOKIE
# 功能：签到、摇一摇、抽奖、白金抽奖、V7升级星钻
# 环境变量配置
IQIYI_COOKIES = os.getenv('IQIYI_COOKIE', '')
NOTIFY_ENABLED = os.getenv('IQIYI_NOTIFY', 'true').lower() == 'true'


class IqiyiCheckIn:
    def __init__(self, cookie, index):
        self.cookie = cookie
        self.index = index
        self.nickname = f"账号{index}"
        self.username = ""
        self.message = []
        self.p00001 = ""
        self.p00002 = ""
        self.p00003 = ""
        self.dfp = ""
        self.qyid = ""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 AppleNews/7.1 iQIYI/15.3.0',
            'Content-Type': 'application/json'
        }
        self.parse_cookie()

    def parse_cookie(self):
        self.p00001 = re.search(r'P00001=([^;]+)', self.cookie).group(1) if re.search(r'P00001=([^;]+)',
                                                                                      self.cookie) else ""
        self.p00002 = re.search(r'P00002=([^;]+)', self.cookie).group(1) if re.search(r'P00002=([^;]+)',
                                                                                      self.cookie) else ""
        self.p00003 = re.search(r'P00003=([^;]+)', self.cookie).group(1) if re.search(r'P00003=([^;]+)',
                                                                                      self.cookie) else ""

        dfp_match = re.search(r'(?:__dfp|dfp)=([^;@]+)', self.cookie)
        self.dfp = dfp_match.group(1).split('@')[0] if dfp_match else ""

        qyid_match = re.search(r'QC005=([^;]+)', self.cookie)
        self.qyid = qyid_match.group(1) if qyid_match else ""

    def get_user_info(self):
        try:
            if self.p00002:
                from urllib.parse import unquote
                user_info = json.loads(unquote(self.p00002))
                self.nickname = user_info.get('nickname', f"账号{self.index}")
                self.username = user_info.get('user_name', '')
                if self.username and len(self.username) > 7:
                    self.username = self.username[:3] + "****" + self.username[7:]
                print(f"✅ [{self.nickname}] 获取用户信息成功")
        except Exception as e:
            print(f"⚠️ [账号{self.index}] 解析用户信息失败: {e}")

    def query_vip_info(self):
        try:
            time.sleep(2)
            url = 'http://serv.vip.iqiyi.com/vipgrowth/query.action'
            params = {'P00001': self.p00001}
            res = requests.get(url, params=params, timeout=10).json()
            if res.get('code') == 'A00000':
                data = res.get('data', {})
                return {
                    'level': data.get('level', 0),
                    'growthvalue': data.get('growthvalue', 0),
                    'distance': data.get('distance', 0),
                    'deadline': data.get('deadline', '非 VIP 用户'),
                    'todayGrowthValue': data.get('todayGrowthValue', 0)
                }
        except Exception as e:
            print(f"⚠️ [{self.nickname}] 查询VIP信息失败: {e}")
        return None

    def lottery(self, award_list=None):
        """摇一摇抽奖 (递归实现)"""
        if award_list is None: award_list = []
        try:
            url = 'https://act.vip.iqiyi.com/shake-api/lottery'
            params = {
                'P00001': self.p00001,
                'deviceID': str(uuid.uuid4()),
                'version': '15.3.0',
                'platform': str(uuid.uuid4())[:16],
                'lotteryType': '0',
                'actCode': '0k9GkUcjqqj4tne8',
                'extendParams': json.dumps({
                    'appIds': 'iqiyi_pt_vip_iphone_video_autorenew_12m_348yuan_v2',
                    'supportSk2Identity': True,
                    'testMode': '0',
                    'iosSystemVersion': '17.4',
                    'bundleId': 'com.qiyi.iphone'
                })
            }
            res = requests.get(url, params=params, timeout=10).json()
            if res.get('code') == 'A00000':
                award_info = res.get('data', {}).get('title', '未知奖励')
                award_list.append(award_info)
                print(f"🎉 [{self.nickname}] 摇一摇获得: {award_info}")
                time.sleep(3)
                return self.lottery(award_list)
            elif res.get('msg') == '抽奖次数用完':
                return "、".join(award_list) if award_list else "抽奖次数用完"
            else:
                return res.get('msg', '摇一摇失败')
        except Exception as e:
            print(f"⚠️ [{self.nickname}] 摇一摇异常: {e}")
            return "、".join(award_list) if award_list else "摇一摇失败"

    def draw(self, draw_type):
        try:
            url = 'https://iface2.iqiyi.com/aggregate/3.0/lottery_activity'
            params = {
                'app_k': 'b398b8ccbaeacca840073a7ee9b7e7e6',
                'app_v': '11.6.5',
                'platform_id': 10,
                'dev_os': '8.0.0',
                'psp_uid': self.p00003,
                'psp_cki': self.p00001,
                'req_sn': int(time.time() * 1000)
            }
            if draw_type == 0: params['lottery_chance'] = 1

            res = requests.get(url, params=params, timeout=10).json()
            if 'code' not in res:
                chance = int(res.get('daysurpluschance', 0))
                msg = res.get('awardName', '')
                return {'status': True, 'msg': msg, 'chance': chance}
            else:
                msg = res.get('kv', {}).get('msg') or res.get('errorReason', '抽奖失败')
                return {'status': False, 'msg': msg, 'chance': 0}
        except Exception as e:
            return {'status': False, 'msg': str(e), 'chance': 0}

    def level_right(self):
        try:
            url = 'https://act.vip.iqiyi.com/level-right/receive'
            data = {'code': 'k8sj74234c683f', 'P00001': self.p00001}
            res = requests.post(url, data=data, timeout=10).json()
            return res.get('msg', '升级失败')
        except Exception as e:
            return str(e)

    def give_times(self):
        url = 'https://pcell.iqiyi.com/lotto/giveTimes'
        codes = ['browseWeb', 'browseWeb', 'bookingMovie']
        for code in codes:
            params = {'actCode': 'bcf9d354bc9f677c', 'timesCode': code, 'P00001': self.p00001}
            try:
                requests.get(url, params=params, timeout=5)
            except:
                pass
            time.sleep(0.5)

    def lotto_lottery(self):
        self.give_times()
        gift_list = []
        url = 'https://pcell.iqiyi.com/lotto/lottery'
        for _ in range(5):
            try:
                params = {'actCode': 'bcf9d354bc9f677c', 'P00001': self.p00001}
                res = requests.get(url, params=params, timeout=10).json()
                gift_name = res.get('data', {}).get('giftName', '')
                if gift_name and '未中奖' not in gift_name:
                    gift_list.append(gift_name)
                time.sleep(1)
            except:
                pass
        return "、".join(gift_list) if gift_list else "未中奖"

    def run(self):
        print(f"\n{'=' * 30}\n开始处理 [{self.nickname}]\n{'=' * 30}")
        if not self.p00001:
            return f"【账号{self.index}】\nCookie无效，缺少P00001"

        self.get_user_info()
        self.message.append(f"👤 用户账号: {self.username}")
        self.message.append(f"📝 用户昵称: {self.nickname}")

        # VIP信息
        vip = self.query_vip_info()
        if vip:
            self.message.extend([
                f"🏆 VIP等级: LV{vip['level']}",
                f"💎 当前成长值: {vip['growthvalue']}",
                f"📈 今日成长值: {vip['todayGrowthValue']}",
                f"⏰ VIP到期: {vip['deadline']}"
            ])

        # 白金抽奖
        self.message.append(f"🎰 白金抽奖: {self.lotto_lottery()}")

        # V7升级
        if vip and vip['deadline'] != '非 VIP 用户':
            self.message.append(f"💎 V7升级星钻: {self.level_right()}")

        # 常规抽奖
        chance_res = self.draw(0)
        chance = chance_res['chance']
        if chance > 0:
            draw_msgs = []
            for _ in range(chance):
                res = self.draw(1)
                if res['status'] and res['msg']: draw_msgs.append(res['msg'])
                time.sleep(1)
            self.message.append(f"🎁 抽奖奖励: {'、'.join(draw_msgs) if draw_msgs else '无'}")
        else:
            self.message.append("🎁 抽奖奖励: 抽奖机会不足")

        # 摇一摇
        self.message.append(f"🎉 每天摇一摇: {self.lottery()}")

        return f"【{self.nickname}】\n" + "\n".join(self.message)


def main():
    if not IQIYI_COOKIES:
        print("❌ 未配置 IQIYI_COOKIE 环境变量！")
        return

    cookies = [c.strip() for c in re.split(r'[&\n]+', IQIYI_COOKIES) if c.strip()]
    print(f"🚀 爱奇艺签到开始，共 {len(cookies)} 个账号\n")

    results = []
    for i, cookie in enumerate(cookies):
        bot = IqiyiCheckIn(cookie, i + 1)
        results.append(bot.run())
        if i < len(cookies) - 1:
            time.sleep(3)

    final_msg = "\n\n" + "=" * 20 + "\n\n".join(results)
    print(final_msg)

    if NOTIFY_ENABLED:
        try:
            from sendNotify import send
            send('🎬 爱奇艺全功能签到', final_msg)
        except ImportError:
            print("⚠️ 未找到 sendNotify.py，跳过推送")


if __name__ == '__main__':
    main()
#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
顺丰速运自动化脚本
来源:
- https://github.com/faintout/myself-script/blob/main/sfsy.py
- https://github.com/Xx1aoy1/scripts/blob/main/sf2.py

功能: 遍历生活特权所有分组的券进行领券，完成任务领取丰蜜积分
变量名: sfsyUrl
格式: 多账号用换行分割
获取方式:
1. 顺丰APP绑定微信后，添加机器人发送“顺丰”
2. 打开小程序或APP-我的-积分，抓包以下URL之一:
   - https://mcs-mimp-web.sf-express.com/mcs-mimp/share/weChat/shareGiftReceiveRedirect
   - https://mcs-mimp-web.sf-express.com/mcs-mimp/share/app/shareRedirect
编码: 抓取URL后，使用 https://www.toolhelper.cn/EncodeDecode/Url 进行编码

Cron: 11 7 * * *
"""

import hashlib
import json
import os
import random
import time
from datetime import datetime, timedelta
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from urllib.parse import unquote

# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 全局日志变量
send_msg = ''
one_msg = ''

def Log(cont=''):
    """记录日志"""
    global send_msg, one_msg
    print(cont)
    if cont:
        one_msg += f'{cont}\n'
        send_msg += f'{cont}\n'

inviteId = ['']

class RUN:
    def __init__(self, info, index):
        """初始化账号信息"""
        global one_msg
        one_msg = ''
        split_info = info.split('@')
        url = split_info[0]
        self.send_UID = split_info[-1] if len(split_info) > 1 and "UID_" in split_info[-1] else None
        self.index = index + 1

        self.s = requests.session()
        self.s.verify = False

        self.headers = {
            'Host': 'mcs-mimp-web.sf-express.com',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090551) XWEB/6945 Flue',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'zh-CN,zh',
            'platform': 'MINI_PROGRAM',
        }

        # 32周年活动相关属性
        self.ifPassAllLevel = False
        self.surplusPushTime = 0
        self.lotteryNum = 0
        self.anniversary_black = False
        self.member_day_black = False
        self.member_day_red_packet_drew_today = False
        self.member_day_red_packet_map = {}
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.max_level = 8
        self.packet_threshold = 1 << (self.max_level - 1)

        self.login_res = self.login(url)

    def get_deviceId(self, characters='abcdef0123456789'):
        """生成随机设备ID"""
        result = ''
        for char in 'xxxxxxxx-xxxx-xxxx':
            if char == 'x':
                result += random.choice(characters)
            else:
                result += char
        return result

    def login(self, sfurl):
        """登录顺丰账号"""
        try:
            ress = self.s.get(sfurl, headers=self.headers)
            self.user_id = self.s.cookies.get_dict().get('_login_user_id_', '')
            self.phone = self.s.cookies.get_dict().get('_login_mobile_', '')
            self.mobile = self.phone[:3] + "*" * 4 + self.phone[7:] if self.phone else ''
            if self.phone:
                Log(f'👤 账号{self.index}:【{self.mobile}】登陆成功')
                return True
            else:
                Log(f'❌ 账号{self.index}获取用户信息失败')
                return False
        except Exception as e:
            Log(f'❌ 登录异常: {str(e)}')
            return False

    def getSign(self):
        """生成请求签名"""
        timestamp = str(int(time.time() * 1000))
        token = 'wwesldfs29aniversaryvdld29'
        sysCode = 'MCS-MIMP-CORE'
        data = f'token={token}×tamp={timestamp}&sysCode={sysCode}'
        signature = hashlib.md5(data.encode()).hexdigest()
        data = {
            'sysCode': sysCode,
            'timestamp': timestamp,
            'signature': signature
        }
        self.headers.update(data)
        return data

    def do_request(self, url, data=None, req_type='post', max_retries=3):
        """发送HTTP请求"""
        self.getSign()
        for retry_count in range(max_retries):
            try:
                if req_type.lower() == 'get':
                    enkelt = self.s.get(url, headers=self.headers, timeout=30)
                elif req_type.lower() == 'post':
                    response = self.s.post(url, headers=self.headers, json=data or {}, timeout=30)
                else:
                    raise ValueError(f'Invalid req_type: {req_type}')

                response.raise_for_status()
                return response.json()

            except (requests.exceptions.RequestException, json.JSONDisposeError) as e:
                Log(f'❌ 请求失败 ({retry_count + 1}/{max_retries}): {str(e)}')
                if retry_count < max_retries - 1:
                    time.sleep(2)
                    continue
                return {'success': False, 'errorMessage': str(e)}
        return {'success': False, 'errorMessage': 'All retries failed'}

    def sign(self):
        """执行签到任务"""
        Log('🎯 开始执行签到')
        json_data = {"comeFrom": "vioin", "channelFrom": "WEIXIN"}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskSignPlusService~automaticSignFetchPackage'
        response = self.do_request(url, data=json_data)
        if response.get('success'):
            count_day = response.get('obj', {}).get('countDay', 0)
            if response.get('obj', {}).get('integralTaskSignPackageVOList'):
                packet_name = response["obj"]["integralTaskSignPackageVOList"][0]["packetName"]
                Log(f'✨ 签到成功，获得【{packet_name}】，本周累计签到【{count_day + 1}】天')
            else:
                Log(f'📝 今日已签到，本周累计签到【{count_day + 1}】天')
        else:
            Log(f'❌ 签到失败！原因：{response.get("errorMessage", "未知错误")}')

    def superWelfare_receiveRedPacket(self):
        """领取超值福利签到奖励"""
        Log('🎁 超值福利签到')
        json_data = {"channel": "czflqdlhbxcx"}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberActLengthy~redPacketActivityService~superWelfare~receiveRedPacket'
        response = self.do_request(url, data=json_data)
        if response.get('success'):
            gift_list = response.get('obj', {}).get('giftList', [])
            if response.get('obj', {}).get('extraGiftList', []):
                gift_list.extend(response['obj']['extraGiftList'])
            gift_names = ', '.join([gift['giftName'] for gift in gift_list]) or '无奖励'
            receive_status = response.get('obj', {}).get('receiveStatus')
            status_message = '领取成功' if receive_status == 1 else '已领取过'
            Log(f'🎉 超值福利签到[{status_message}]: {gift_names}')
        else:
            Log(f'❌ 超值福利签到失败: {response.get("errorMessage", "未知错误")}')

    def get_SignTaskList(self, end=False):
        """获取签到任务列表"""
        Log('🎯 开始获取签到任务列表' if not end else '💰 查询最终积分')
        json_data = {"channelType": "1", "deviceId": self.get_deviceId()}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskStrategyService~queryPointTaskAndSignFromES'
        response = self.do_request(url, data=json_data)
        if response.get('success') and response.get('obj'):
            totalPoint = response["obj"]["totalPoint"]
            Log(f'💰 {"执行前" if not end else "当前"}积分：【{totalPoint}】')
            if not end:
                for task in response["obj"]["taskTitleLevels"]:
                    self.taskId = task["taskId"]
                    self.taskCode = task["taskCode"]
                    self.strategyId = task["strategyId"]
                    self.title = task["title"]
                    status = task["status"]
                    skip_title = ['用行业模板寄件下单', '去新增一个收件偏好', '参与积分活动']
                    if status == 3:
                        Log(f'✨ {self.title}-已完成')
                        continue
                    if self.title in skip_title:
                        Log(f'⏭️ {self.title}-跳过')
                        continue
                    self.doTask()
                    time.sleep(2)
                    self.receiveTask()

    def doTask(self):
        """完成签到任务"""
        Log(f'🎯 开始去完成【{self.title}】任务')
        json_data = {"taskCode": self.taskCode}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonRoutePost/memberEs/taskRecord/finishTask'
        response = self.do_request(url, data=json_data)
        Log(f'✨ 【{self.title}】任务-{"已完成" if response.get("success") else response.get("errorMessage", "失败")}')

    def receiveTask(self):
        """领取签到任务奖励"""
        Log(f'🎁 开始领取【{self.title}】任务奖励')
        json_data = {
            "strategyId": self.strategyId,
            "taskId": self.taskId,
            "taskCode": self.taskCode,
            "deviceId": self.get_deviceId()
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskStrategyService~fetchIntegral'
        response = self.do_request(url, data=json_data)
        Log(f'✨ 【{self.title}】任务奖励-{"领取成功" if response.get("success") else response.get("errorMessage", "失败")}')

    def do_honeyTask(self):
        """完成丰蜜任务"""
        Log(f'🎯 开始完成【{self.taskType}】任务')
        json_data = {"taskCode": self.taskCode}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberEs~taskRecord~finishTask'
        response = self.do_request(url, data=json_data)
        Log(f'✨ 【{self.taskType}】任务-{"已完成" if response.get("success") else response.get("errorMessage", "失败")}')

    def receive_honeyTask(self):
        """领取丰蜜任务奖励"""
        Log(f'🎁 领取【{self.taskType}】丰蜜任务')
        self.headers.update({
            'syscode': 'MCS-MIMP-CORE',
            'channel': 'wxwdsj',
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json;charset=UTF-8',
            'platform': 'MINI_PROGRAM'
        })
        json_data = {"taskType": self.taskType}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeIndexService~receiveHoney'
        response = self.do_request(url, data=json_data)
        Log(f'✨ 收取任务【{self.taskType}】-{"成功" if response.get("success") else response.get("errorMessage", "失败")}')

    def get_coupom(self, goods):
        """领取优惠券"""
        json_data = {
            "from": "Point_Mall",
            "orderSource": "POINT_MALL_EXCHANGE",
            "goodsNo": goods['goodsNo'],
            "quantity": 1,
            "taskCode": self.taskCode
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~pointMallService~createOrder'
        response = self.do_request(url, data=json_data)
        return response.get('success')

    def get_coupom_list(self):
        """获取优惠券列表"""
        json_data = {"memGrade": 2, "categoryCode": "SHTQ", "showCode": "SHTQWNTJ"}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~mallGoodsLifeService~list'
        response = self.do_request(url, data=json_data)
        if response.get('success'):
            all_goods = []
            for obj in response.get("obj", []):
                all_goods.extend(obj.get("goodsList", []))
            for goods in all_goods:
                if goods.get('exchangeTimesLimit', 0) >= 1:
                    if self.get_coupom(goods):
                        Log('✨ 成功领取券，任务结束！')
                        return
            Log('📝 所有券尝试完成，没有可用的券或全部领取失败。')
        else:
            Log(f'❌ 获取券列表失败！原因：{response.get("errorMessage", "未知错误")}')

    def get_honeyTaskListStart(self):
        """获取丰蜜任务列表"""
        Log('🍯 开始获取采蜜换大礼任务列表')
        self.headers['channel'] = 'wxwdsj'
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeIndexService~taskDetail'
        response = self.do_request(url, data={})
        if response.get('success'):
            for item in response["obj"]["list"]:
                self.taskType = item["taskType"]
                status = item["status"]
                if status == 3:
                    Log(f'✨ 【{self.taskType}】-已完成')
                    continue
                if "taskCode" in item:
                    self.taskCode = item["taskCode"]
                    if self.taskType == 'DAILY_VIP_TASK_TYPE':
                        self.get_coupom_list()
                    else:
                        self.do_honeyTask()
                if self.taskType == 'BEES_GAME_TASK_TYPE':
                    self.honey_damaoxian()
                time.sleep(2)

    def honey_damaoxian(self):
        """执行大冒险任务"""
        Log('>>> 执行大冒险任务')
        gameNum = 5
        for i in range(1, gameNum + 1):
            json_data = {"gatherHoney": 20}
            Log(f'>> 开始第{i}次大冒险')
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeGameService~gameReport'
            response = self.do_request(url, data=json_data)
            if response.get('success'):
                gameNum = response.get('obj')['gameNum']
                Log(f'> 大冒险成功！剩余次数【{gameNum}】')
                time.sleep(2)
            elif response.get("errorMessage") == '容量不足':
                Log('> 需要扩容')
                self.honey_expand()
            else:
                Log(f'> 大冒险失败！【{response.get("errorMessage", "未知错误")}】')
                break

    def honey_expand(self):
        """容器扩容"""
        Log('>>> 容器扩容')
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeIndexService~expand'
        response = self.do_request(url, data={})
        if response.get('success'):
            Log(f'> 成功扩容【{response.get("obj", "未知")}】容量')
        else:
            Log(f'> 扩容失败！【{response.get("errorMessage", "未知错误")}】')

    def honey_indexData(self, end=False):
        """执行采蜜换大礼任务"""
        Log('🍯 开始执行采蜜换大礼任务' if not end else '🍯 查询最终丰蜜')
        random_invite = random.choice([invite for invite in inviteId if invite != self.user_id])
        self.headers['channel'] = 'wxwdsj'
        json_data = {"inviteUserId": random_invite}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeIndexService~indexData'
        response = self.do_request(url, data=json_data)
        if response.get('success'):
            usableHoney = response.get('obj').get('usableHoney')
            activityEndTime = response.get('obj').get('activityEndTime', '')
            if not end:
                Log(f'📅 本期活动结束时间【{activityEndTime}】')
                Log(f'🍯 执行前丰蜜：【{usableHoney}】')
                for task in response.get('obj').get('taskDetail', []):
                    self.taskType = task['type']
                    self.receive_honeyTask()
                    time.sleep(2)
            else:
                Log(f'🍯 执行后丰蜜：【{usableHoney}】')

    def EAR_END_2023_TaskList(self):
        """执行年终集卡任务"""
        Log('🎭 开始年终集卡任务')
        json_data = {"activityCode": "YEAREND_2024", "channelType": "MINI_PROGRAM"}
        self.headers.update({'channel': '24nzdb', 'platform': 'MINI_PROGRAM', 'syscode': 'MCS-MIMP-CORE'})
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~taskList'
        response = self.do_request(url, data=json_data)
        if response.get('success'):
            for item in response["obj"]:
                self.title = item["taskName"]
                self.taskType = item["taskType"]
                status = item["status"]
                if status == 3:
                    Log(f'✨ 【{self.taskType}】-已完成')
                    continue
                if self.taskType == 'INTEGRAL_EXCHANGE':
                    self.EAR_END_2023_ExchangeCard()
                elif self.taskType == 'CLICK_MY_SETTING':
                    self.taskCode = item["taskCode"]
                    self.addDeliverPrefer()
                if "taskCode" in item:
                    self.taskCode = item["taskCode"]
                    self.doTask()
                    time.sleep(2)
                    self.EAR_END_2023_receiveTask()
                else:
                    Log(f'⚠️ 暂时不支持【{self.title}】任务')

    def EAR_END_2023_ExchangeCard(self):
        """年终集卡兑换"""
        Log('>>> 执行年终集卡兑换')
        # 占位符，需补充具体兑换逻辑
        pass

    def EAR_END_2023_receiveTask(self):
        """领取年终集卡任务奖励"""
        Log(f'🎁 领取年终集卡【{self.title}】任务奖励')
        json_data = {"taskCode": self.taskCode, "activityCode": "YEAREND_2024"}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~fetchTaskReward'
        response = self.do_request(url, data=json_data)
        Log(f'✨ 【{self.title}】任务奖励-{"领取成功" if response.get("success") else response.get("errorMessage", "失败")}')

    def activityTaskService_taskList(self):
        """获取32周年活动任务列表"""
        Log('🎭 开始32周年活动任务')
        json_data = {"activityCode": "DRAGONBOAT_2025", "channelType": "MINI_PROGRAM"}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~taskList'
        response = self.do_request(url, data=json_data)
        if response.get('success'):
            skip_task_types = [
                'PLAY_ACTIVITY_GAME', 'SEND_SUCCESS_RECALL', 'OPEN_SUPER_CARD',
                'CHARGE_NEW_EXPRESS_CARD', 'OPEN_NEW_EXPRESS_CARD', 'OPEN_FAMILY_CARD', 'INTEGRAL_EXCHANGE'
            ]
            task_list = [x for x in response.get('obj', []) if x.get('status') == 2 and x.get('taskType') not in skip_task_types]
            if not task_list:
                Log('📝 没有可执行的任务')
                return
            Log(f'📝 获取到未完成任务: {len(task_list)}个')
            for task in task_list:
                Log(f'📝 开始任务: {task.get("taskName")} [{task.get("taskType")}]')
                time.sleep(random.uniform(1.5, 3))
                self.activityTaskService_finishTask(task)
                time.sleep(1.5)
        else:
            Log(f'❌ 获取活动任务失败: {response.get("errorMessage", "未知错误")}')

    def activityTaskService_finishTask(self, task):
        """完成32周年活动任务"""
        json_data = {"taskCode": task.get('taskCode')}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberEs~taskRecord~finishTask'
        response = self.do_request(url, data=json_data)
        Log(f'📝 完成任务[{task.get("taskName")}]: {"成功" if response.get("success") else response.get("errorMessage", "失败")}')

    def dragonBoatGame2025ServiceWin(self, levelIndex):
        """完成龙舟游戏关卡"""
        json_data = {"levelIndex": levelIndex}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~dragonBoatGame2025Service~win'
        response = self.do_request(url, data=json_data)
        Log(f'🎮 第{levelIndex}关通关-{"成功" if response.get("success") else response.get("errorMessage", "失败")}')

    def dragonBoat2025HastenService(self):
        """查询龙舟加速状态"""
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~dragonBoat2025HastenService~getHastenStatus'
        response = self.do_request(url, data={})
        if response.get('success'):
            self.lotteryNum = response.get('obj', {}).get('remainHastenChance', 0)
            Log(f'🎲 剩余加速次数: {self.lotteryNum}')
        else:
            Log(f'❌ 查询加速次数失败: {response.get("errorMessage", "未知错误")}')

    def hastenLottery(self):
        """执行龙舟加速抽奖"""
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~dragonBoat2025HastenService~hastenLottery'
        response = self.do_request(url, data={})
        if response.get('success'):
            remain = response.get('obj', {}).get('remainHastenChance', 0)
            Log(f'🎲 加速成功，剩余加速次数: {remain}')
        else:
            Log(f'❌ 加速失败: {response.get("errorMessage", "未知错误")}')

    def prizeDraw(self, opt):
        """领取龙舟活动奖励"""
        json_data = {"currency": opt.get('currency')}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~dragonBoat2025LotteryService~prizeDraw'
        response = self.do_request(url, data=json_data)
        if response.get('success'):
            gift_name = response.get('obj', {}).get('giftBagName', '未知奖励')
            Log(f'🎁 抽奖获得: {gift_name}')
        else:
            Log(f'❌ 抽奖失败: {response.get("errorMessage", "未知错误")}')

    def getUpgradeStatus(self):
        """查询龙舟活动升级状态"""
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~dragonBoat2025UpgradeService~getUpgradeStatus'
        response = self.do_request(url, data={})
        if response.get('success'):
            current_ratio = response.get('obj', {}).get('currentRatio', 0)
            level_list = [x for x in response.get('obj', {}).get('levelList', []) if x.get('balance', 0) > 0]
            if level_list:
                Log(f'🎯 当前进度: {current_ratio}%，已达到兑换条件')
                for item in level_list:
                    self.prizeDraw(item)
                    time.sleep(1.5)
            else:
                Log(f'⏳ 当前进度: {current_ratio}%')
        else:
            Log(f'❌ 查询加速状态失败: {response.get("errorMessage", "未知错误")}')

    def activityTaskService_integralExchange(self):
        """执行积分兑换"""
        json_data = {"exchangeNum": 1, "activityCode": "DRAGONBOAT_2025"}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~dragonBoat2025TaskService~integralExchange'
        response = self.do_request(url, data=json_data)
        Log(f'✅ 积分兑换-{"成功" if response.get("success") else response.get("errorMessage", "失败")}')

    def dragonBoatGame2025Service(self):
        """获取龙舟游戏信息"""
        json_data = {"channelType": "MINI_PROGRAM"}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~dragonBoatGame2025Service~indexInfo'
        response = self.do_request(url, data=json_data)
        if response.get('success'):
            self.surplusPushTime = response.get('obj', {}).get('surplusPushTime', 0)
            self.ifPassAllLevel = response.get('obj', {}).get('ifPassAllLevel', False)
            Log(f'🎮 剩余游戏次数: {self.surplusPushTime}')
            return True
        Log(f'❌ 访问失败: {response.get("errorMessage", "未知错误")}')
        return False

    def addDeliverPrefer(self):
        """新增收件偏好"""
        Log(f'>>> 开始【{self.title}】任务')
        json_data = {
            "country": "中国",
            "countryCode": "A000086000",
            "province": "北京市",
            "provinceCode": "A110000000",
            "city": "北京市",
            "cityCode": "A111000000",
            "county": "东城区",
            "countyCode": "A110101000",
            "address": "1号楼1单元101",
            "latitude": "",
            "longitude": "",
            "memberId": "",
            "locationCode": "010",
            "zoneCode": "CN",
            "postCode": "",
            "takeWay": "7",
            "callBeforeDelivery": 'false',
            "deliverTag": "2,3,4,1",
            "deliverTagContent": "",
            "startDeliverTime": "",
            "selectCollection": 'false',
            "serviceName": "",
            "serviceCode": "",
            "serviceType": "",
            "serviceAddress": "",
            "serviceDistance": "",
            "serviceTime": "",
            "serviceTelephone": "",
            "channelCode": "RW11111",
            "taskId": self.taskId,
            "extJson": "{\"noDeliverDetail\":[]}"
        }
        url = 'https://ucmp.sf-express.com/cx-wechat-member/member/deliveryPreference/addDeliverPrefer'
        response = self.do_request(url, data=json_data)
        Log(f'✨ 新增一个收件偏好-{"成功" if response.get("success") else response.get("errorMessage", "失败")}')

    def member_day_index(self):
        """执行会员日活动"""
        Log('🎭 会员日活动')
        invite_user_id = random.choice([invite for invite in inviteId if invite != self.user_id])
        payload = {'inviteUserId': invite_user_id}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayIndexService~index'
        response = self.do_request(url, data=payload)
        if response.get('success'):
            lottery_num = response.get('obj', {}).get('lotteryNum', 0)
            can_receive_invite_award = response.get('obj', {}).get('canReceiveInviteAward', False)
            if can_receive_invite_award:
                self.member_day_receive_invite_award(invite_user_id)
            self.member_day_red_packet_status()
            Log(f'🎁 会员日可以抽奖{lottery_num}次')
            for _ in range(lottery_num):
                self.member_day_lottery()
            if self.member_day_black:
                return
            self.member_day_task_list()
            if self.member_day_black:
                return
            self.member_day_red_packet_status()
        else:
            error_message = response.get('errorMessage', '无返回')
            Log(f'📝 查询会员日失败: {error_message}')
            if '没有资格参与活动' in error_message:
                self.member_day_black = True
                Log('📝 会员日任务风控')

    def member_day_receive_invite_award(self, invite_user_id):
        """领取会员日邀请奖励"""
        payload = {'inviteUserId': invite_user_id}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayIndexService~receiveInviteAward'
        response = self.do_request(url, data=payload)
        if response.get('success'):
            product_name = response.get('obj', {}).get('productName', '空气')
            Log(f'🎁 会员日奖励: {product_name}')
        else:
            error_message = response.get('errorMessage', '无返回')
            Log(f'📝 领取会员日奖励失败: {error_message}')
            if '没有资格参与活动' in error_message:
                self.member_day_black = True
                Log('📝 会员日任务风控')

    def member_day_lottery(self):
        """会员日抽奖"""
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayLotteryService~lottery'
        response = self.do_request(url, data={})
        if response.get('success'):
            product_name = response.get('obj', {}).get('productName', '空气')
            Log(f'🎁 会员日抽奖: {product_name}')
        else:
            error_message = response.get('errorMessage', '无返回')
            Log(f'📝 会员日抽奖失败: {error_message}')
            if '没有资格参与活动' in error_message:
                self.member_day_black = True
                Log('📝 会员日任务风控')

    def member_day_task_list(self):
        """获取会员日任务列表"""
        payload = {'activityCode': 'MEMBER_DAY', 'channelType': 'MINI_PROGRAM'}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~taskList'
        response = self.do_request(url, data=payload)
        if response.get('success'):
            task_list = response.get('obj', [])
            for task in task_list:
                if task['status'] == 1:
                    if self.member_day_black:
                        return
                    self.member_day_fetch_mix_task_reward(task)
                elif task['status'] == 2 and task['taskType'] not in [
                    'SEND_SUCCESS', 'INVITEFRIENDS_PARTAKE_ACTIVITY', 'OPEN_SVIP',
                    'OPEN_NEW_EXPRESS_CARD', 'OPEN_FAMILY_CARD', 'CHARGE_NEW_EXPRESS_CARD', 'INTEGRAL_EXCHANGE'
                ]:
                    for _ in range(task['restFinishTime']):
                        if self.member_day_black:
                            return
                        self.member_day_finish_task(task)
        else:
            error_message = response.get('errorMessage', '无返回')
            Log(f'📝 查询会员日任务失败: {error_message}')
            if '没有资格参与活动' in error_message:
                self.member_day_black = True
                Log('📝 会员日任务风控')

    def member_day_finish_task(self, task):
        """完成会员日任务"""
        payload = {'taskCode': task['taskCode']}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberEs~taskRecord~finishTask'
        response = self.do_request(url, data=payload)
        if response.get('success'):
            Log(f'📝 完成会员日任务[{task["taskName"]}]: 成功')
            self.member_day_fetch_mix_task_reward(task)
        else:
            error_message = response.get('errorMessage', '无返回')
            Log(f'📝 完成会员日任务[{task["taskName"]}]: {error_message}')
            if '没有资格参与活动' in error_message:
                self.member_day_black = True
                Log('📝 会员日任务风控')

    def member_day_fetch_mix_task_reward(self, task):
        """领取会员日任务奖励"""
        payload = {'taskType': task['taskType'], 'activityCode': 'MEMBER_DAY', 'channelType': 'MINI_PROGRAM'}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~fetchMixTaskReward'
        response = self.do_request(url, data=payload)
        Log(f'🎁 领取会员日任务[{task["taskName"]}]: {"成功" if response.get("success") else response.get("errorMessage", "失败")}')

    def member_day_receive_red_packet(self, hour):
        """领取会员日红包"""
        payload = {'receiveHour': hour}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayTaskService~receiveRedPacket'
        response = self.do_request(url, data=payload)
        Log(f'🎁 会员日领取{hour}点红包-{"成功" if response.get("success") else response.get("errorMessage", "失败")}')

    def member_day_red_packet_status(self):
        """查询会员日红包状态"""
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayPacketService~redPacketStatus'
        response = self.do_request(url, data={})
        if response.get('success'):
            packet_list = response.get('obj', {}).get('packetList', [])
            self.member_day_red_packet_map = {packet['level']: packet['count'] for packet in packet_list}
            for level in range(1, self.max_level):
                count = self.member_day_red_packet_map.get(level, 0)
                while count >= 2:
                    self.member_day_red_packet_merge(level)
                    count -= 2
            packet_summary = [f"[{level}]X{count}" for level, count in self.member_day_red_packet_map.items() if count > 0]
            Log(f"📝 会员日合成列表: {', '.join(packet_summary) or '无红包'}")
            if self.member_day_red_packet_map.get(self.max_level):
                Log(f"🎁 会员日已拥有[{self.max_level}级]红包X{self.member_day_red_packet_map[self.max_level]}")
                self.member_day_red_packet_draw(self.max_level)
            else:
                remaining_needed = sum(1 << (int(level) - 1) for level, count in self.member_day_red_packet_map.items() if count > 0)
                remaining = self.packet_threshold - remaining_needed
                Log(f"📝 会员日距离[{self.max_level}级]红包还差: [1级]红包X{remaining}")
        else:
            error_message = response.get('errorMessage', '无返回')
            Log(f'📝 查询会员日合成失败: {error_message}')
            if '没有资格参与活动' in error_message:
                self.member_day_black = True
                Log('📝 会员日任务风控')

    def member_day_red_packet_merge(self, level):
        """合成会员日红包"""
        payload = {'level': level, 'num': 2}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayPacketService~redPacketMerge'
        response = self.do_request(url, data=payload)
        if response.get('success'):
            Log(f'🎁 会员日合成: [{level}级]红包X2 -> [{level + 1}级]红包')
            self.member_day_red_packet_map[level] = self.member_day_red_packet_map.get(level, 0) - 2
            self.member_day_red_packet_map[level + 1] = self.member_day_red_packet_map.get(level + 1, 0) + 1
        else:
            Log(f'📝 会员日合成[{level}级]红包失败: {response.get("errorMessage", "无返回")}')

    def member_day_red_packet_draw(self, level):
        """提取会员日红包"""
        payload = {'level': str(level)}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayPacketService~redPacketDraw'
        response = self.do_request(url, data=payload)
        if response.get('success'):
            coupon_names = [item['couponName'] for item in response.get('obj', [])] or ['空气']
            Log(f"🎁 会员日提取[{level}级]红包: {', '.join(coupon_names)}")
        else:
            Log(f"📝 会员日提取[{level}级]红包失败: {response.get('errorMessage', '无返回')}")

    def main(self):
        """主执行逻辑"""
        if not self.login_res:
            return False
        time.sleep(random.uniform(1, 3))

        # 执行签到任务
        self.sign()
        self.superWelfare_receiveRedPacket()
        self.get_SignTaskList()
        self.get_SignTaskList(True)

        # 执行丰蜜任务
        self.get_honeyTaskListStart()
        self.honey_indexData()
        self.honey_indexData(True)

        # 检查活动截止时间
        activity_end_date = get_quarter_end_date()
        days_left = (activity_end_date - datetime.now()).days
        Log(f"⏰ 采蜜活动截止兑换还有{days_left}天，请及时进行兑换！！")

        # 执行32周年活动任务
        try:
            self.activityTaskService_taskList()
            self.activityTaskService_integralExchange()
            if self.dragonBoatGame2025Service() and not self.ifPassAllLevel:
                for index in range(1, 5):
                    self.dragonBoatGame2025ServiceWin(index)
                    time.sleep(1.5)
            self.dragonBoat2025HastenService()
            while self.lotteryNum > 0:
                self.hastenLottery()
                time.sleep(1)
                self.getUpgradeStatus()
                self.lotteryNum -= 1
        except Exception as e:
            Log(f'❌ 32周年活动执行异常: {str(e)}')

        # 年终集卡任务
        if datetime.now() < datetime(2025, 4, 8, 19, 0):
            self.EAR_END_2023_TaskList()
        else:
            Log('🎭 周年庆活动已结束')

        # 会员日任务
        if 26 <= datetime.now().day <= 28:
            self.member_day_index()
        else:
            Log('⏰ 未到指定时间不执行会员日任务')

        self.sendMsg()
        return True

    def sendMsg(self, help=False):
        """发送通知（占位符）"""
        pass

def get_quarter_end_date():
    """计算当前季度结束日期"""
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    next_quarter_first_day = datetime(current_year, ((current_month - 1) // 3 + 1) * 3 + 1, 1)
    return next_quarter_first_day - timedelta(days=1)

if __name__ == '__main__':
    """主程序入口"""
    APP_NAME = '顺丰速运'
    ENV_NAME = 'sfsyUrl'
    token = os.getenv(ENV_NAME)
    tokens = token.split('\n') if token else []
    if tokens:
        Log(f"🚚 共获取到{len(tokens)}个账号")
        for index, infos in enumerate(tokens):
            Log(f"==================================\n🚚 处理账号{index + 1}")
            RUN(infos, index).main()
    else:
        Log("❌ 未获取到sfsyUrl环境变量")

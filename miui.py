#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/just_for_happy
# @Time : 2023/2/27 13:23
# -------------------------------
# cron "30 8,10,15 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('小米社区任务得成长值')
# 4.11 更新了请求后获取cookie失败的问题 基本一次性就可以跑完 不用多跑几次

import requests, json ,time,base64,binascii,hashlib,os,re

# 小米签到 小米社区任务得成长值
# 配置帐号密码 一一对应 按需增删 不对上会出错 若帐号密码填写没有错误 还是报错应该是账号在非常用设备上登录, 需要验证码, 使用该设备安装图形化工具后自行前去验证https://web-alpha.vip.miui.com/page/info/mio/mio/internalTest 图形化工具怎么安装可参考https://cloud.tencent.com/developer/article/2069955
# 青龙变量export mi_account='' export mi_password=''

# 青龙变量 mi_account mi_password
mi_account = os.getenv("mi_account").split('&')
mi_password = os.getenv("mi_password").split('&')

#获取cookie
def Phone(account, password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    Hash = md5.hexdigest()
    url = "https://account.xiaomi.com/pass/serviceLoginAuth2"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent":
        "Dalvik/2.1.0 (Linux; U; Android 12; M2007J17C Build/SKQ1.211006.001) APP/xiaomi.vipaccount APPV/220301 MK/UmVkbWkgTm90ZSA5IFBybw== PassportSDK/3.7.8 passport-ui/3.7.8",
        "Cookie":
        "deviceId=X0jMu7b0w-jcne-S; pass_o=2d25bb648d023d7f; sdkVersion=accountsdk-2020.01.09",
        "Host": "account.xiaomi.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    data = {
        "cc": "+86",
        "qs": "%3F_json%3Dtrue%26sid%3Dmiui_vip%26_locale%3Dzh_CN",
        "callback": "https://api.vip.miui.com/sts",
        "_json": "true",
        "user": account,
        "hash": Hash.upper(),
        "sid": "miui_vip",
        "_sign": "ZJxpm3Q5cu0qDOMkKdWYRPeCwps%3D",
        "_locale": "zh_CN"
    }
    Auth1 = requests.post(url=url, headers=headers,
                         data=data).text.replace("&&&START&&&", "")
    Auth = json.loads(Auth1)
    ssecurity = Auth["ssecurity"]
    nonce = Auth["nonce"]
    sha1 = hashlib.sha1()
    Str = "nonce=" + str(nonce) + "&" + ssecurity
    sha1.update(Str.encode("utf-8"))
    clientSign = base64.encodebytes(
        binascii.a2b_hex(sha1.hexdigest().encode("utf-8"))).decode(
            encoding="utf-8").strip()
    nurl = Auth[
        "location"] + "&_userIdNeedEncrypt=true&clientSign=" + clientSign

    resp = requests.get(url=nurl)
    return requests.utils.dict_from_cookiejar(resp.cookies)



for i in range(len(mi_account)):
    c_list = []
    for k in range(10):
        a = Phone(mi_account[i], mi_password[i])
        if len(a) > 0:
            c_list.append(a)
    cookie = str(c_list[-1]).replace('{','').replace('}','').replace(',',';').replace(': ','=').replace('\'','').replace(' ','')
    miui_vip_ph = "".join(re.findall('miui_vip_ph=(.*?);', cookie, re.S))
    url = 'https://api.vip.miui.com/mtop/planet/vip/user/checkinV2?ref=vipAccountShortcut&pathname=/mio/checkIn&version=dev.231107'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
        'Cookie': f'{cookie}'
    }
    user_url = 'https://api.vip.miui.com/api/community/user/home/page'
    params = {
            'miui_vip_ph': miui_vip_ph
    }
    html = requests.get(url=url, headers=headers,params=params)
    html_user = requests.get(url=user_url, headers=headers)
    result = json.loads(html.text)
    result_user = json.loads(html_user.text)
    userId = result_user['entity']['userId']
    print('*************'+'\n'+f'开始第{i + 1}个账号签到'+'\n'+'签到结果：')
    print(result['message'])
    print('userId: '+userId + ' 用户名: '+result_user['entity']['userName']+ ' 段位: '+ result_user['entity']['userGrowLevelInfo']['showLevel'])


# 点赞任务
    print('开始加入点赞任务>>>>')
    for a in range(2):
        dzurl = 'https://api.vip.miui.com/mtop/planet/vip/content/announceThumbUp'
        dz_data = {
        'postId': '36625780',
        'sign': '36625780',
        'timestamp':int(round(time.time() * 1000))
        }
        dz_html = requests.get(url=dzurl, headers=headers,data=dz_data)
        dz_result = json.loads(dz_html.text)
        if dz_result['status'] == 200:
            print('点赞帖子成功成功')
        time.sleep(1)
#加入圈子
    print('开始加入圈子任务>>>>')
    unfollow_url = 'https://api.vip.miui.com/api/community/board/unfollow?boardId=558495'
    html_unfollow = requests.get(url=unfollow_url, headers=headers)
    result_unfollow = json.loads(html_user.text)
    if result_unfollow['status']==200:
        print('退出圈子成功')
    time.sleep(1)

    follow_url = 'https://api.vip.miui.com/api/community/board/follow?boardId=558495'
    html_follow = requests.get(url=follow_url, headers=headers)
    result_follow = json.loads(html_user.text)
    if result_follow['status']==200:
        print('加入圈子成功')
    time.sleep(1)

# 浏览主页
    info_url =f'https://api.vip.miui.com/mtop/planet/vip/member/addCommunityGrowUpPointByAction?userId={userId}&action=BROWSE_SPECIAL_PAGES_USER_HOME'
    html_info = requests.get(url=info_url, headers=headers)
    time.sleep(12)
    result_info = json.loads(html_info.text)
    if result_info['status'] == 200:
        print('浏览主页成功，获得积分： '+str(result_info['entity']['score']))
    else:
        print(result_info['message']+'，今日已达上限')
#浏览专题
    print('开始浏览专题任务>>>>')
    llzt_url = f'https://api.vip.miui.com/mtop/planet/vip/member/addCommunityGrowUpPointByAction?userId={userId}&action=BROWSE_SPECIAL_PAGES_SPECIAL_PAGE'
    html_llzt = requests.get(url=llzt_url, headers=headers)
    time.sleep(12)
    result_llzt = json.loads(html_llzt.text)
    # print(result_llzt)
    if result_llzt['status'] == 200:
        print('浏览主页成功，获得积分： '+str(result_llzt['entity']['score']))
    else:
        print(result_llzt['message']+'，今日已达上限')

#浏览帖子
    print('开始浏览帖子任务>>>>')
    for a in range(3):
        watch_url = f'https://api.vip.miui.com/mtop/planet/vip/member/addCommunityGrowUpPointByAction?userId={userId}&action=BROWSE_POST_10S'
        html_watch = requests.get(url=watch_url, headers=headers)
        time.sleep(12)
        result_watch = json.loads(html_watch.text)
        # print(result_watch)
        if result_watch['status'] == 200:
            print('浏览帖子成功，获得积分： ' + str(result_watch['entity']['score']))
        else:
            print(result_watch['message'] + '，今日已达上限')
#拔萝卜
    carroturl ='https://api.vip.miui.com/api/carrot/pull'
    resp_carrot = requests.post(url=carroturl, headers=headers,params=params)
    r_json = resp_carrot.json()
    if r_json['code'] == 401:
        print("社区拔萝卜失败：Cookie无效")
    elif r_json['code'] != 200:
        print("社区拔萝卜失败：" + str(r_json['entity']['message']))
    print("社区拔萝卜结果：" + str(r_json['entity']['message']))
    money_count = r_json['entity']['header']['moneyCount']
    print("当前金币数：" + str(money_count))

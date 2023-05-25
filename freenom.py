#!/usr/bin/env python3
# _*_ coding:utf-8 _*_

'''
cron: 33 7 * * 2,5
new Env:('freenom多帐户续期');
'''

import requests
import re,os,time,random

# 配置环境变量：export freenom_usr=""，多号用&分割，示例：123@qq.com&abc@163.com
# 配置环境变量：export freenom_psd=""，账号对应密码同样用&分割，示例：miam1&mima2
# 密码含&的，设置export change_split="",示例：export change_split=","代表用逗号分割


# 登录url
LOGIN_URL = 'https://my.freenom.com/dologin.php'
# 域名状态url
DOMAIN_STATUS_URL = 'https://my.freenom.com/domains.php?a=renewals'
# 续期url
RENEW_DOMAIN_URL = 'https://my.freenom.com/domains.php?submitrenewals=true'
# 登录匹配
token_ptn = re.compile('name="token" value="(.*?)"', re.I)
domain_info_ptn = re.compile(
    r'<tr><td>(.*?)</td><td>[^<]+</td><td>[^<]+<span class="[^<]+>(\d+?).Days</span>[^&]+&domain=(\d+?)">.*?</tr>',
    re.I)
login_status_ptn = re.compile('<a href="logout.php">Logout</a>', re.I)
sess = requests.Session()
sess.headers.update({
    'user-agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/103.0.5060.134 Safari/537.36'
})
sess.headers.update({
    'content-type': 'application/x-www-form-urlencoded',
    'referer': 'https://my.freenom.com/clientarea.php'
})


def main(usr,psd):
    try:  # 异常捕捉
        r = sess.post(LOGIN_URL, data={'username': usr, 'password': psd})
        if r.status_code != 200:
            print('Can not login. Pls check network.')
            return
        # 查看域名状态
        sess.headers.update({'referer': 'https://my.freenom.com/clientarea.php'})
        r = sess.get(DOMAIN_STATUS_URL)
    except:
        print('Network failed.')
        return
    # 确认登录状态
    if not re.search(login_status_ptn, r.text):
        print('login failed, retry')
        return
    # 获取token
    page_token = re.search(token_ptn, r.text)
    if not page_token:
        print('page_token missed')
        return
    token = page_token.group(1)
    # 获取域名列表
    domains = re.findall(domain_info_ptn, r.text)
    domains_list = []
    renew_domains_succeed = []
    renew_domains_failed = []
    # 域名续期
    for domain, days, renewal_id in domains:
        day_s = int(days)
        domains_list.append(f'域名:{domain}还有{day_s}天到期~')
        if day_s < 14:
            # 避免频繁操作
            time.sleep(6)
            sess.headers.update({
                'referer':
                f'https://my.freenom.com/domains.php?a=renewdomain&domain={renewal_id}',
                'content-type': 'application/x-www-form-urlencoded'
            })
            try:
                r = sess.post(RENEW_DOMAIN_URL,
                              data={
                                  'token': token,
                                  'renewalid': renewal_id,
                                  f'renewalperiod[{renewal_id}]': '12M',
                                  'paymentmethod': 'credit'
                              })
            except:
                print('Network failed.')
                renew_domains_failed.append(domain)
                continue
            if r.text.find('Order Confirmation') != -1:
                renew_domains_succeed.append(domain)
            else:
                renew_domains_failed.append(domain)

    # 输出结果并推送通知
    print(domains_list, renew_domains_succeed, renew_domains_failed)

if __name__ == '__main__':
    usrs = os.getenv("freenom_usr").split('&')
    psds = os.getenv("freenom_psd").split('&')

    if len(usrs) != len(psds):
        print('Can not metch. Pls check export')
        exit(-1)
    print(f'--------共{len(usrs)}个账号--------\n')
    for i in range(len(usrs)):
        print(f'***第{i + 1}个账号: {usrs[i]} ***\n')
        # 随机暂停几秒，错峰使用
        time.sleep(random.randint(1,30))
        main(usrs[i], psds[i])



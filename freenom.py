#!/usr/bin/env python3
# _*_ coding:utf-8 _*_

# 觉得好用请点 *star*，作者仓库:https://github.com/rpgrpg/freenom-qinglong.git

'''
cron: 33 7 * * 2,5
new Env:('freenom多帐户续期');
'''
# 配置环境变量：export freenom_usr=""，多号用&分割，示例：123@qq.com&abc@163.com
# 配置环境变量：export freenom_psd=""，账号对应密码同样用&分割，示例：miam1&mima2
# 密码含&的，设置export change_split="",示例：export change_split=","代表用逗号分割
# V20231a

import requests
import re,os,time,random
try:
    from notify import send
except:
    print("upload notify failed")


# 没有设置环境变量可以在此处直接填写freenom用户名，多号用&分割，示例：'123@qq.com&abc@163.com'
username = ''
# 没有设置环境变量可以在此处直接填写freenom密码，账号对应密码同样用&分割，示例：'psd1&psd2'
password = ''
# 密码含&的，设置echa_split = '' ,示例：cha_split = ','代表用逗号分割
cha_split = ''
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

# 获取用户列表
def get_usr():
    #  先检测环境变量
    if "freenom_usr" in os.environ:
        # 配置环境变量：export FREENOM_USR=""，多号用&分割
        usr_list = os.environ["freenom_usr"].split("&")
        return usr_list
    # 从脚本内获取
    elif username:
        usr_list = username.split('&')
        return usr_list
    # 都没有
    print('Pls config export OR fill in username.')
    send('未在环境变量或脚本中找到账号信息，请手动添加')
    exit(-1)

# 获取密码
def get_psd():
    if "freenom_psd" in os.environ:
        if "change_split" in os.environ:
            psd_list = os.environ["freenom_psd"].split(os.environ["change_split"])
            return psd_list
        else:
            # 配置环境变量：export FREENOM_PSD=""，多号用&分割
            psd_list = os.environ["freenom_psd"].split("&")
            return psd_list
    # 从脚本内获取
    elif password:
        if cha_split:
            psd_list = password.split(cha_split)
            return psd_list
        else:
            psd_list = password.split('&')
            return psd_list
    # 都没有
    print('Pls config export OR fill in password.')
    send('未在环境变量或脚本中找到密码信息，请手动添加')
    exit(-1)

# start
def main(usr,psd):
    try:  # 异常捕捉
        r = sess.post(LOGIN_URL, data={'username': usr, 'password': psd})
        if r.status_code != 200:
            print('Can not login. Pls check network.')
            send('登录失败，', '请检查网络')
            return
        # 查看域名状态
        sess.headers.update({'referer': 'https://my.freenom.com/clientarea.php'})
        r = sess.get(DOMAIN_STATUS_URL)
    except:
        print('Network failed.')
        send('连接中断，', '请检查网络是否正常')
        return
    # 确认登录状态
    if not re.search(login_status_ptn, r.text):
        print('login failed, retry')
        send('登录失败，', '请检查账号有效性')
        return
    # 获取token
    page_token = re.search(token_ptn, r.text)
    if not page_token:
        print('page_token missed')
        send('连接中断，', '请检查网络是否正常')
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
                send('连接中断，', '请检查网络是否正常')
                renew_domains_failed.append(domain)
                continue
            if r.text.find('Order Confirmation') != -1:
                renew_domains_succeed.append(domain)
            else:
                renew_domains_failed.append(domain)

    # 输出结果并推送通知
    print(domains_list, renew_domains_succeed, renew_domains_failed)
    if renew_domains_failed:
        send(f'注意！！！您有{len(renew_domains_failed)}个域名续期失败，请及时手动操作确认！', f'续期失败的域名：{renew_domains_failed}')
    else:
        if renew_domains_succeed:
            send(f'账号{usr}共有{len(domains_list)}个域名:\n{domains_list}', f'域名: {renew_domains_succeed}续期成功！')
        else:
            send('恭喜，两周内没有需要续期的域名', f'账号{usr}共有{len(domains_list)}个域名:\n{domains_list}')
    return

if __name__ == '__main__':
    usrs = get_usr()
    psds = get_psd()

    if len(usrs) != len(psds):
        print('Can not metch. Pls check export')
        send('账号密码数量不匹配,请检查变量, ' , '密码含&的添加change_split变量或更改密码')
        exit(-1)
    print(f'--------共{len(usrs)}个账号--------\n')
    for i in range(len(usrs)):
        print(f'***第{i + 1}个账号: {usrs[i]} ***\n')
        # 随机暂停几秒，错峰使用
        time.sleep(random.randint(1,30))
        main(usrs[i], psds[i])



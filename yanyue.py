import requests, re, json

# 企业微信推送参数
corpid = ''
agentid = ''
corpsecret = ''
touser = ''
# 推送加 token
plustoken = ''

# 多账号的话cookie
#配置cookie https://bbs.yanyue.cn/plugin.php?id=signgame:signgame 登录后抓取cookie填入下面 多账号填多个
cookie = [
    "cookie1",
    "cookie2"
]

def Push(contents):
    # 微信推送
    if all([corpid, agentid, corpsecret, touser]):
        token = \
        requests.get(f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}').json()[
            'access_token']
        json = {"touser": touser, "msgtype": "text", "agentid": agentid, "text": {"content": "烟悦网打卡\n" + contents}}
        resp = requests.post(f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}", json=json)
        print('微信推送成功' if resp.json()['errmsg'] == 'ok' else '微信推送失败')

    if plustoken:
        headers = {'Content-Type': 'application/json'}
        json = {"token": plustoken, 'title': '烟悦网打卡', 'content': contents.replace('\n', '<br>'), "template": "json"}
        resp = requests.post(f'http://www.pushplus.plus/send', json=json, headers=headers).json()
        print('push+推送成功' if resp['code'] == 200 else 'push+推送失败')


massage_list =[]

for i in range(len(cookie)):
    url = 'https://bbs.yanyue.cn/plugin.php?id=signgame:signgame'
    sign_url = 'https://bbs.yanyue.cn/plugin.php?id=signgame:signgame&optype=checkin'
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'content-length': '131',
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        'cookie': f'{cookie[i]}'
    }
    data = {
        'checktoken': ''
    }
    html = requests.post(url=url, headers=headers,data=data).text
    checktoken = str(re.findall('<input type=\'hidden\' name=\'checktoken\' value=(.*?)><p>', str(html), re.S)).replace('[','').replace(']','').replace('\'','')#获取token
    sign_data = {
        'checktoken': f'{checktoken}'
    }
    result = requests.post(url=sign_url, headers=headers,data=sign_data).text #检查签到情况
    html_2 = requests.post(url=url, headers=headers,data=data).text
    name = str(re.findall('" target="_blank" title="访问我的空间">(.*?)</a></strong>', str(html_2), re.S)).replace('[','').replace(']','').replace('\'','')
    info = str(re.findall('<p>（午夜12点后刷新页面<font color=red>此处</font>将显示报到按钮）</p><p>(.*?)本页最后刷新服务器时间', str(html_2), re.S))
    information = '帐号'+str(i+1) +' 用户名：'+name + ' '+re.sub('([^\u4e00-\u9fa5\u0030-\u0039])', ' ', info).replace('  ','').replace('3000',' ')
    massage_list.append(information)

massage =str(massage_list).replace("\', \'","\n").replace('[','').replace(']','').replace('\'','')
print(massage)
# Push(contents=massage)

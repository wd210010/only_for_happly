import requests,json,re

# 青龙变量 cjwlhck  
# 微信小程序 》》》》  #小程序://春茧未来荟/YjaFJZ4TMwoBd6a 
# 打开后注册会员 抓包program.springcocoon.com域名的请求同里面的cookie填入青龙变量 config.sh 里export ='' 多账号&分割  或新建变量里面 多号新建多个 

cjwlhck = os.getenv("cjwlhck").split('&')
cookielist =cjwlhck.split('&')

for i in range(len(cookielist)):
    print(f'开始第{i+1}个账号签到')
    if cookielist[i][-1] !=';':
            newcookie =  cookielist[i]+';'
            X_XSRF_TOKEN = re.findall('XSRF-TOKEN=(.*?);', newcookie, re.S)[0]
    headers ={
        'Host':'program.springcocoon.com',
        'Accept':'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With':'XMLHttpRequest',
        'Accept-Language':'zh-CN,zh-Hans;q=0.9',
        'Accept-Encoding':'gzip, deflate, br',
        'X-XSRF-TOKEN':X_XSRF_TOKEN,
        'Content-Type':'application/x-www-form-urlencoded',
        'Origin':'https://program.springcocoon.com',
        'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.45(0x18002d25) NetType/WIFI Language/zh_CN miniProgram/wx6b10d95e92283e1c',
        'Referer':'https://program.springcocoon.com/szbay/AppInteract/SignIn/Index?isWeixinRegister=true',
        'Content-Length':'91',
        'Connection':'keep-alive',
        'Cookie':cookielist[i]
    }
    data ='id=6c3a00f6-b9f0-44a3-b8a0-d5d709de627d&webApiUniqueID=f2cca2a7-c327-1d76-d375-ec92cdd296cd'
    try:
        resp = requests.post('https://program.springcocoon.com/szbay/api/services/app/SignInRecord/SignInAsync',headers=headers,data=data)
        result = json.loads(resp.text)
        if result['success'] == False:
            msg =result['error']['message']
            print(f'签到失败：{msg}')
        else:
            point = result['result']['listSignInRuleData'][0]['point']
            print(f'签到成功获得万象星：{str(point)}个')
    except:
        print('该账号失效！')

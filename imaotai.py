#!/usr/bin/python3
# -- coding: utf-8 --
# @Time : 2023/05/03 10:23
# -------------------------------
# cron "1,30 9 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('小茅预约');

import datetime #line:1
import os #line:2
import random #line:3
import time #line:4
import re #line:5
import requests #line:6
import base64 #line:7
import json #line:8

#原创 微信公众号@爱上羊毛侠 

# 青龙面板加入环境变量MTTokenD
# MTTokenD是茅台预约参数，多个请换行，格式'省份,城市,经度,维度,设备id,token,MT-Token-Wap(抓包小茅运)'

p_c_map ={}#line:1
mt_r ='clips_OlU6TmFRag5rCXwbNAQ/Tz1SKlN8THcecBp/'#line:2
res_map ={'10213':'贵州茅台酒（癸卯兔年）','2476':'贵州茅台酒（壬寅虎年）','10214':'贵州茅台酒（癸卯兔年）x2'}#line:7
def mt_add (OOOOO0O00O00O0000 ,OOO00OOO0O00OO00O ,OOOO00000O00OO0O0 ,O00000O0OO00OO00O ,OO0OO0000O000O0O0 ,O0OO000O00O0OO00O ):#line:10
    O00OO000OOOOO0OO0 =f'{int(time.time() * 1000)}'#line:11
    OOOO0OOO0OO0O000O =requests .get (f'http://82.157.10.108:8086/get_mtv?DeviceID={O0OO000O00O0OO00O}&MTk={O00OO000OOOOO0OO0}&version={mt_version}&key=yaohuo')#line:13
    OO000O00O0000OO00 ={'User-Agent':'iPhone 14','MT-Token':OO0OO0000O000O0O0 ,'MT-Network-Type':'WIFI','MT-User-Tag':'0','MT-R':mt_r ,'MT-Lat':'','MT-K':O00OO000OOOOO0OO0 ,'MT-Lng':'','MT-Info':'028e7f96f6369cafe1d105579c5b9377','MT-APP-Version':mt_version ,'MT-Request-ID':f'{int(time.time() * 1000)}','Accept-Language':'zh-Hans-CN;q=1','MT-Device-ID':O0OO000O00O0OO00O ,'MT-V':OOOO0OOO0OO0O000O .text ,'MT-Bundle-ID':'com.moutai.mall','mt-lng':lng ,'mt-lat':lat }#line:23
    OOOO0O0O0000000O0 ={"itemInfoList":[{"count":1 ,"itemId":str (OOOOO0O00O00O0000 )}],"sessionId":OOOO00000O00OO0O0 ,"userId":str (O00000O0OO00OO00O ),"shopId":str (OOO00OOO0O00OO00O )}#line:25
    OOOO0OOO0OO0O000O =requests .get ('http://82.157.10.108:8086/get_actParam?key=yaohuo&actParam='+base64 .b64encode (json .dumps (OOOO0O0O0000000O0 ).replace (' ','').encode ('utf8')).decode ())#line:27
    OOOO0O0O0000000O0 ['actParam']=OOOO0OOO0OO0O000O .text #line:28
    O00OO0OOO00OOO0OO =OOOO0O0O0000000O0 #line:29
    OOO0OO0OO00O00OO0 =requests .post ('https://app.moutai519.com.cn/xhr/front/mall/reservation/add',headers =OO000O00O0000OO00 ,json =O00OO0OOO00OOO0OO )#line:31
    O0OOOO0OOO0OO0OOO =OOO0OO0OO00O00OO0 .json ().get ('code',0 )#line:32
    if O0OOOO0OOO0OO0OOO ==2000 :#line:33
        return OOO0OO0OO00O00OO0 .json ().get ('data',{}).get ('successDesc',"未知")#line:34
    return '申购失败:'+OOO0OO0OO00O00OO0 .json ().get ('message',"未知原因")#line:35
def tongzhi (OOO0O0O0O0OOOO0OO ):#line:38
    OOOOOOO0O0O000OO0 =os .getenv ('mtec_user','').split (',')#line:39
    for OO0O0000OOO0O0000 in OOOOOOO0O0O000OO0 :#line:40
        O0OOOOO0O000000OO ='http://wxpusher.zjiecode.com/api/send/message/?appToken=&content={}&uid={}'.format (OOO0O0O0O0OOOO0OO ,OO0O0000OOO0O0000 )#line:42
        O000O0O0O0OOO0O00 =requests .get (O0OOOOO0O000000OO )#line:43
        print (O000O0O0O0OOO0O00 .text )#line:44
def get_session_id (O0O0O00OO00OO0OOO ,O000O0OOO0OOOO0O0 ):#line:47
    OO0OOOOOOO00O0000 ={'mt-device-id':O0O0O00OO00OO0OOO ,'mt-user-tag':'0','accept':'*/*','mt-network-type':'WIFI','mt-token':O000O0OOO0OOOO0O0 ,'mt-bundle-id':'com.moutai.mall','accept-language':'zh-Hans-CN;q=1','mt-request-id':f'{int(time.time() * 1000)}','mt-app-version':mt_version ,'user-agent':'iPhone 14','mt-r':mt_r ,'mt-lng':lng ,'mt-lat':lat }#line:62
    O00OO00O0OOO000OO =requests .get ('https://static.moutai519.com.cn/mt-backend/xhr/front/mall/index/session/get/'+time_keys ,headers =OO0OOOOOOO00O0000 )#line:65
    OOOO00O00OO00OOOO =O00OO00O0OOO000OO .json ().get ('data',{}).get ('sessionId')#line:66
    O00OOO0OOOOOOO0OO =O00OO00O0OOO000OO .json ().get ('data',{}).get ('itemList',[])#line:67
    O0O000O0O0O0O00OO =[OO0OOOO0OOO0000OO .get ('itemCode')for OO0OOOO0OOO0000OO in O00OOO0OOOOOOO0OO ]#line:68
    return OOOO00O00OO00OOOO ,O0O000O0O0O0O00OO #line:69
def get_shop_item (OO000O0OOOOOO00OO ,OOO0O0O0O00OO0OOO ,O00000O000000000O ,O0OOO0O0O0O0O00OO ,OOO0O000OO0000000 ,OO0OOOO000OO00OOO ):#line:72
    O000OO0000OOO00O0 ={'mt-device-id':O00000O000000000O ,'mt-user-tag':'0','mt-lat':'','accept':'*/*','mt-network-type':'WIFI','mt-token':O0OOO0O0O0O0O00OO ,'mt-bundle-id':'com.moutai.mall','accept-language':'zh-Hans-CN;q=1','mt-request-id':f'{int(time.time() * 1000)}','mt-r':mt_r ,'mt-app-version':mt_version ,'user-agent':'iPhone 14','mt-lng':lng ,'mt-lat':lat }#line:88
    OO00OOOO00OOOO0OO =requests .get ('https://static.moutai519.com.cn/mt-backend/xhr/front/mall/shop/list/slim/v3/'+str (OO000O0OOOOOO00OO )+'/'+OOO0O000OO0000000 +'/'+str (OOO0O0O0O00OO0OOO )+'/'+time_keys ,headers =O000OO0000OOO00O0 )#line:93
    O00OO0OO00O0OOO00 =OO00OOOO00OOOO0OO .json ().get ('data',{})#line:94
    OO0O0OO00OOOO000O =O00OO0OO00O0OOO00 .get ('shops',[])#line:95
    OO000OOO00OO0OO00 =p_c_map [OOO0O000OO0000000 ][OO0OOOO000OO00OOO ]#line:96
    for O0O0O0O00OO0O0OO0 in OO0O0OO00OOOO000O :#line:97
        if not O0O0O0O00OO0O0OO0 .get ('shopId')in OO000OOO00OO0OO00 :#line:98
            continue #line:99
        if OOO0O0O0O00OO0OOO in str (O0O0O0O00OO0O0OO0 ):#line:100
            return O0O0O0O00OO0O0OO0 .get ('shopId')#line:101
def get_user_id (O0O00O0O0OOOO0OO0 ,O0OOOO0OO0000O000 ):#line:104
    OOOO0OO0O0OOOOOO0 ={'MT-User-Tag':'0','Accept':'*/*','MT-Network-Type':'WIFI','MT-Token':O0O00O0O0OOOO0OO0 ,'MT-Bundle-ID':'com.moutai.mall','Accept-Language':'zh-Hans-CN;q=1, en-CN;q=0.9','MT-Request-ID':f'{int(time.time() * 1000)}','MT-APP-Version':mt_version ,'User-Agent':'iOS;16.0.1;Apple;iPhone 14 ProMax','MT-R':mt_r ,'MT-Device-ID':O0OOOO0OO0000O000 ,'mt-lng':lng ,'mt-lat':lat }#line:119
    OOOOO0O0OOO00000O =requests .get ('https://app.moutai519.com.cn/xhr/front/user/info',headers =OOOO0OO0O0OOOOOO0 )#line:122
    O00O000000OOO000O =OOOOO0O0OOO00000O .json ().get ('data',{}).get ('userName')#line:123
    O00OOO0O0OOO00O0O =OOOOO0O0OOO00000O .json ().get ('data',{}).get ('userId')#line:124
    OO0O00OOO0OOOOOO0 =OOOOO0O0OOO00000O .json ().get ('data',{}).get ('mobile')#line:125
    return O00O000000OOO000O ,O00OOO0O0OOO00O0O ,OO0O00OOO0OOOOOO0 #line:126
def getUserEnergyAward (O0OO0000O0000OOO0 ,OOO000O0OO0OO0000 ):#line:129
    """
    领取耐力
    :return:
    """#line:133
    OO00OOOO0O0O0O000 ={'MT-Device-ID-Wap':O0OO0000O0000OOO0 ,'MT-Token-Wap':OOO000O0OO0OO0000 ,'YX_SUPPORT_WEBP':'1',}#line:139
    O0OOO0OOO0O000OO0 ={'X-Requested-With':'XMLHttpRequest','User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2_1 like Mac OS X)','Referer':'https://h5.moutai519.com.cn/gux/game/main?appConfig=2_1_2','Client-User-Agent':'iOS;15.0.1;Apple;iPhone 12 ProMax','MT-R':mt_r ,'Origin':'https://h5.moutai519.com.cn','MT-APP-Version':mt_version ,'MT-Request-ID':f'{int(time.time() * 1000)}','Accept-Language':'zh-CN,zh-Hans;q=0.9','MT-Device-ID':O0OO0000O0000OOO0 ,'Accept':'application/json, text/javascript, */*; q=0.01','mt-lng':lng ,'mt-lat':lat }#line:155
    OO00OOO0000O0O000 =requests .post ('https://h5.moutai519.com.cn/game/isolationPage/getUserEnergyAward',cookies =OO00OOOO0O0O0O000 ,headers =O0OOO0OOO0O000OO0 ,json ={})#line:157
    return OO00OOO0000O0O000 .json ().get ('message')if '无法领取奖励'in OO00OOO0000O0O000 .text else "领取奖励成功"#line:158
def get_map ():#line:161
    global p_c_map #line:162
    O0O0O00000O000OOO ='https://static.moutai519.com.cn/mt-backend/xhr/front/mall/resource/get'#line:163
    O00O00000O0OO00O0 ={'X-Requested-With':'XMLHttpRequest','User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0_1 like Mac OS X)','Referer':'https://h5.moutai519.com.cn/gux/game/main?appConfig=2_1_2','Client-User-Agent':'iOS;16.0.1;Apple;iPhone 14 ProMax','MT-R':mt_r ,'Origin':'https://h5.moutai519.com.cn','MT-APP-Version':mt_version ,'MT-Request-ID':f'{int(time.time() * 1000)}{random.randint(1111111, 999999999)}{int(time.time() * 1000)}','Accept-Language':'zh-CN,zh-Hans;q=1','MT-Device-ID':f'{int(time.time() * 1000)}{random.randint(1111111, 999999999)}{int(time.time() * 1000)}','Accept':'application/json, text/javascript, */*; q=0.01','mt-lng':lng ,'mt-lat':lat }#line:178
    OOOOOOOOO000O0000 =requests .get (O0O0O00000O000OOO ,headers =O00O00000O0OO00O0 ,)#line:179
    OO0OOO0O0O00000OO =OOOOOOOOO000O0000 .json ().get ('data',{}).get ('mtshops_pc',{})#line:180
    O0OO00O0OOOOOOO00 =OO0OOO0O0O00000OO .get ('url')#line:181
    OO0O0O0O00000OOOO =requests .get (O0OO00O0OOOOOOO00 )#line:182
    for OO00000OO0O0O0O00 ,O0O0000OO0O000OO0 in dict (OO0O0O0O00000OOOO .json ()).items ():#line:183
        O00O00O000OOOOO0O =O0O0000OO0O000OO0 .get ('provinceName')#line:184
        O00000OO000OOOO0O =O0O0000OO0O000OO0 .get ('cityName')#line:185
        if not p_c_map .get (O00O00O000OOOOO0O ):#line:186
            p_c_map [O00O00O000OOOOO0O ]={}#line:187
        if not p_c_map [O00O00O000OOOOO0O ].get (O00000OO000OOOO0O ,None ):#line:188
            p_c_map [O00O00O000OOOOO0O ][O00000OO000OOOO0O ]=[OO00000OO0O0O0O00 ]#line:189
        else :#line:190
            p_c_map [O00O00O000OOOOO0O ][O00000OO000OOOO0O ].append (OO00000OO0O0O0O00 )#line:191
    return p_c_map #line:192
def login (O0000OOOOOOO0O0O0 ,OOOO00O0OO0OO00OO ,O0O0O0OO0000OOOO0 ):#line:195
    """

    :param phone: 手机号
    :param vCode: 验证码
    :param Device_ID: 设备id
    :return:
    """#line:202
    O0O00OO00O0OO0O0O =f'{int(time.time() * 1000)}'#line:203
    OOOOOO000O00OO0O0 =requests .get (f'http://82.157.10.108:8086/get_mtv?DeviceID={O0O0O0OO0000OOOO0}&MTk={O0O00OO00O0OO0O0O}&version={mt_version}&key=yaohuo')#line:205
    O0OOO00OO00O0OOO0 ={'MT-Device-ID':O0O0O0OO0000OOOO0 ,'MT-User-Tag':'0','Accept':'*/*','MT-Network-Type':'WIFI','MT-Token':'','MT-K':O0O00OO00O0OO0O0O ,'MT-Bundle-ID':'com.moutai.mall','MT-V':OOOOOO000O00OO0O0 .text ,'User-Agent':'iOS;16.0.1;Apple;iPhone 14 ProMax','Accept-Language':'zh-Hans-CN;q=1','MT-Request-ID':f'{int(time.time() * 1000)}18342','MT-R':mt_r ,'MT-APP-Version':mt_version ,}#line:220
    OO000O000OO0O0OO0 ={'ydToken':'','mobile':f'{O0000OOOOOOO0O0O0}','vCode':f'{OOOO00O0OO0OO00OO}','ydLogId':'',}#line:227
    OOO00O00O00000O0O =requests .post ('https://app.moutai519.com.cn/xhr/front/user/register/login',headers =O0OOO00OO00O0OOO0 ,json =OO000O000OO0O0OO0 )#line:230
    OO0O00O00OO0O000O =OOO00O00O00000O0O .json ().get ('data',{})#line:231
    OOO00O000O0O00O00 =OO0O00O00OO0O000O .get ('token')#line:232
    O000OOO0OO0O0O000 =OO0O00O00OO0O000O .get ('cookie')#line:233
    print (O0O0O0OO0000OOOO0 ,OOO00O000O0O00O00 ,O000OOO0OO0O0O000 )#line:234
    return O0O0O0OO0000OOOO0 ,OOO00O000O0O00O00 ,O000OOO0OO0O0O000 #line:235

def Push(contents):
  # plustoken推送
    headers = {'Content-Type': 'application/json'}
    json = {"token": plustoken, 'title': '茅台预约推送', 'content': contents.replace('\n', '<br>'), "template": "json"}
    resp = requests.post(f'http://www.pushplus.plus/send', json=json, headers=headers).json()
    print('push+推送成功' if resp['code'] == 200 else 'push+推送失败')
    
if __name__ =='__main__':#line:245
    plustoken =os .getenv ("plustoken")#line:246
    mt_tokens =os .getenv ("MTTokenD")#line:247
    mt_version ="".join (re .findall ('new__latest__version">(.*?)</p>',requests .get ('https://apps.apple.com/cn/app/i%E8%8C%85%E5%8F%B0/id1600482450').text ,re .S )).replace ('版本 ','')#line:248
    print ('当前最新版本为:'+mt_version )#line:249
    if not mt_tokens :#line:250
        print ('MTToken is null')#line:251
        exit ()#line:252
    mt_token_list =mt_tokens .split ('&')#line:253
    s ="-------------------总共"+str (int (len (mt_token_list )))+"个用户-------------------"+'\n'#line:256
    userCount =0 #line:257
    if len (mt_token_list )>0 :#line:258
        for mt_token in mt_token_list :#line:259
            userCount +=1 #line:260
            province ,city ,lng ,lat ,device_id ,token ,ck =mt_token .split (',')#line:262
            time_keys =str (int (time .mktime (datetime .date .today ().timetuple ()))*1000 )#line:264
            get_map ()#line:265
            try :#line:267
                sessionId ,itemCodes =get_session_id (device_id ,token )#line:268
                userName ,user_id ,mobile =get_user_id (token ,device_id )#line:269
                if not user_id :#line:270
                    s +="第"+str (userCount )+"个用户token失效，请重新登录"+'\n'#line:271
                    continue #line:272
                s +="第"+str (userCount )+"个用户----------------"+userName +'_'+mobile +"开始任务"+"----------------"+'\n'#line:274
                for itemCode in itemCodes :#line:275
                    name =res_map .get (str (itemCode ))#line:276
                    if name :#line:277
                        shop_id =get_shop_item (sessionId ,itemCode ,device_id ,token ,province ,city )#line:279
                        res =mt_add (itemCode ,str (shop_id ),sessionId ,user_id ,token ,device_id )#line:281
                        s +=itemCode +'_'+name +'---------------'+res +'\n'#line:283
                if not ck :#line:284
                    r =getUserEnergyAward (device_id ,ck )#line:285
                    s +=userName +'_'+mobile +'---------------'+"小茅运:"+r +'\n'#line:287
                s +=userName +'_'+mobile +"正常结束任务"+'\n              \n'#line:288
            except Exception as e :#line:289
                s +=userName +'_'+mobile +"异常信息"+e #line:290
    print (s )#line:291
    Push (contents =s )#line:292

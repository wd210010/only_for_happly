#!/usr/bin/python3
# -- coding: utf-8 -- 
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/only_for_happly
# @Time : 2024/05/14 9:23
# -------------------------------
# cron "15 20 6,15 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('百度贴吧')

#变量为百度贴吧登录后的ck全部 变量名为tieback

import hashlib
import re,os

import requests


class Tieba:
    def __init__(self, check_items):
        self.check_items = check_items

    @staticmethod
    def login_info(session):
        return session.get("https://zhidao.baidu.com/api/loginInfo").json()

    def valid(self, session):
        try:
            res = session.get("http://tieba.baidu.com/dc/common/tbs").json()
        except Exception as e:
            return False, f"登录验证异常，错误信息: {e}"
        if res["is_login"] == 0:
            return False, "登录失败，cookie 异常"
        tbs = res["tbs"]
        user_name = self.login_info(session=session)["userName"]
        return tbs, user_name

    @staticmethod
    def tieba_list_more(session):
        res = session.get(
            "https://tieba.baidu.com/f/like/mylike?&pn=1",
            timeout=(5, 20),
            allow_redirects=False,
        ).text
        try:
            pn = int(
                re.match(r".*/f/like/mylike\?&pn=(.*?)\">尾页.*", res, re.S | re.I)[1]
            )

        except Exception:
            pn = 1
        pattern = re.compile(r".*?<a href=\"/f\?kw=.*?title=\"(.*?)\">")
        for next_page in range(2, pn + 2):
            yield from pattern.findall(res)
            res = session.get(
                f"https://tieba.baidu.com/f/like/mylike?&pn={next_page}",
                timeout=(5, 20),
                allow_redirects=False,
            ).text

    def get_tieba_list(self, session):
        return list(self.tieba_list_more(session))

    @staticmethod
    def sign(session, tb_name_list, tbs):
        success_count, error_count, exist_count, shield_count = 0, 0, 0, 0
        for tb_name in tb_name_list:
            md5 = hashlib.md5(
                f"kw={tb_name}tbs={tbs}tiebaclient!!!".encode("utf-8")
            ).hexdigest()
            data = {"kw": tb_name, "tbs": tbs, "sign": md5}
            try:
                res = session.post(
                    url="http://c.tieba.baidu.com/c/c/forum/sign", data=data
                ).json()
                if res["error_code"] == "0":
                    success_count += 1
                elif res["error_code"] == "160002":
                    exist_count += 1
                elif res["error_code"] == "340006":
                    shield_count += 1
                else:
                    error_count += 1
            except Exception as e:
                print(f"贴吧 {tb_name} 签到异常，原因{str(e)}")
        return (
            f"贴吧总数: {len(tb_name_list)}\n"
            f"签到成功: {success_count}\n"
            f"已经签到: {exist_count}\n"
            f"被屏蔽的: {shield_count}\n"
            f"签到失败: {error_count}"
        )

    def main(self):
        msg_all = ""
        for check_item in self.check_items:
            cookie = {
                item.split("=")[0]: item.split("=")[1]
                for item in check_item.get("cookie").split("; ")
            }
            session = requests.session()
            session.cookies.update(cookie)
            session.headers.update({"Referer": "https://www.baidu.com/"})
            tbs, user_name = self.valid(session)
            if tbs:
                tb_name_list = self.get_tieba_list(session)
                msg = f"帐号信息: {user_name}\n{self.sign(session, tb_name_list, tbs)}"
            else:
                msg = f"帐号信息: {user_name}\n签到状态: Cookie 可能过期"
            msg_all += msg + "\n\n"
        return msg_all


def string_to_dict(s):
    parts = s.split('#')
    result_dict = {}
    result_dict['cookie'] = parts[0]
    return result_dict

def start():
    s = os.getenv("tieback").split('#')
    print(f'共{len(s)}个账号')
    for i in range(len(s)):
        item =s[i]
        _check_items = [string_to_dict(item)]
        result = Tieba(check_items=_check_items).main()
        print(result)

if __name__ == "__main__":
    start()

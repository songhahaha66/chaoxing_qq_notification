import configparser

import requests
from bs4 import BeautifulSoup
class xxt:
    def __init__(self,account,password):
        self.req = requests.Session()
        self.req.headers = {
            "Accept-Encoding": "gzip",
            "Accept-Language": "zh-Hans-CN;q=1, zh-Hant-CN;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        }
        url = f"https://passport2-api.chaoxing.com/v11/loginregister?code={password}&cx_xxt_passport=json&uname={account}&loginType=1&roleSelect=true"
        res = self.req.get(url)
        if res.json()['mes'] == "验证通过":
            # 获取Cookie
            cookie = requests.utils.dict_from_cookiejar(self.req.cookies)
            mycookie = ""
            for key, value in cookie.items():
                mycookie += f"{key}={value};"
            self.req.headers["Cookie"] = mycookie
            print("初始化登录成功")

    def get_all_homework(self):
        res=self.req.get("http://mooc1-api.chaoxing.com/work/stu-work")
        page = BeautifulSoup(res.text, 'html.parser')
        result = []
        for i in page.find_all("li"):
            homework_name = i.find("p").text
            homework_status = i.find_all("span")[0].text
            subject = i.find_all("span")[1].text
            url = i['data']
            try:
                taskrefId = url.split('taskrefId=')[1].split('&')[0]
            except:
                taskrefId = None
            if homework_status != "未提交":
                result.append({"subject":subject,"homework_name":homework_name, "homework_status":homework_status, "url":url, "taskrefId":taskrefId})
            else:
                r = self.req.get(url)
                p = BeautifulSoup(r.text, 'html.parser')
                deadline = p.find_all("h4")[1].text[5:]
                result.append({"subject":subject,"homework_name":homework_name, "homework_status":homework_status, "url":url, "deadline":deadline, "taskrefId":taskrefId})
        return result

    def get_all_exam(self):
        res2=self.req.get("https://mooc1-api.chaoxing.com/exam/phone/examcode")
        page = BeautifulSoup(res2.text, 'html.parser')
        result = []
        for i in page.find_all("li"):
            exam_name = i.find("dl").find("dt").text
            exam_status = i.find("span").text
            url = i['data']
            result.append({"exam_name":exam_name, "exam_status":exam_status, "url":url})
        return result

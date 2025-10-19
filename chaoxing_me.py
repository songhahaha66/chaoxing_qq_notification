import configparser
import re
import datetime

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
        res = self.req.get("http://mooc1-api.chaoxing.com/work/stu-work")
        page = BeautifulSoup(res.text, 'html.parser')
        result = []

        for i in page.find_all("li"):
            # 跳过没有data属性的li标签
            if not i.has_attr('data'):
                continue

            # 获取基本信息
            url = i['data']

            # 获取作业名称
            p_tag = i.find("p")
            if not p_tag:
                continue
            homework_name = p_tag.get_text(strip=True)

            # 获取所有span标签
            spans = i.find_all("span")
            if len(spans) < 2:
                continue

            # 获取作业状态（第一个span，如果有class="status"优先）
            homework_status = None
            for span in spans:
                if span.has_attr('class') and 'status' in span.get('class', []):
                    homework_status = span.get_text(strip=True)
                    break
            if not homework_status:
                homework_status = spans[0].get_text(strip=True)

            # 获取科目名称（第二个span）
            subject = spans[1].get_text(strip=True)

            # 获取剩余时间信息（如果有class="fr"的span）
            remaining_time = None
            for span in spans:
                if span.has_attr('class') and 'fr' in span.get('class', []):
                    remaining_time = span.get_text(strip=True)
                    break

            # 提取taskrefId
            taskrefId = None
            try:
                if 'taskrefId=' in url:
                    taskrefId = url.split('taskrefId=')[1].split('&')[0]
            except:
                pass

            # 构建作业信息
            homework_info = {
                "subject": subject,
                "homework_name": homework_name,
                "homework_status": homework_status,
                "url": url,
                "taskrefId": taskrefId
            }

            # 如果有剩余时间信息，添加到结果中
            if remaining_time:
                homework_info["remaining_time"] = remaining_time

            # 如果是未提交的作业，根据剩余时间计算截止时间
            if homework_status == "未提交":
                deadline = None

                # 如果没有获取到截止时间，根据剩余时间计算
                if not deadline and remaining_time:
                    # 解析剩余时间格式，如 "剩余166小时3分钟"
                    time_match = re.search(r'剩余(\d+)小时(\d+)分钟', remaining_time)
                    if time_match:
                        hours = int(time_match.group(1))
                        minutes = int(time_match.group(2))
                        # 计算截止时间
                        deadline_time = datetime.datetime.now() + datetime.timedelta(hours=hours, minutes=minutes)
                        deadline = deadline_time.strftime("%Y-%m-%d %H:%M")
                        homework_info["deadline"] = deadline

            result.append(homework_info)

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

    def get_homework_detail_url(self, url):
        req = self.req.get(url)
        page = BeautifulSoup(req.text, 'html.parser')
        scripts = page.find_all("script")
        for script in scripts:
            pattern = r"(/work/phone/doHomeWork\?[^']+)"
            match = re.search(pattern, str(script.string))
            if match:
                url = match.group(1)
                url = "https://mooc1-api.chaoxing.com/mooc-ans" + url
                print(url)
                return url

    def get_homework_detail_info(self, detail_url):
        res = self.req.get(detail_url)
        page = BeautifulSoup(res.text, 'html.parser')
        result = []
        for i in page.find_all("div",class_="pad30"):
            question = i.find("h2",class_="titType").text
            description = ''
            for d in i.find_all('p'):
                description += d.text
            result.append({"question":question,"description":description})
        return result

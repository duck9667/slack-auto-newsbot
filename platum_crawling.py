import time
import requests
import datetime
import json
from bs4 import BeautifulSoup

# 합치기
def getNews(keyword_list, days, n) : 
    keyword_list =  keyword_list # 키워드 설정
    n = n # 키워드당 n개
    days = days # 최근 n일

    # 크롤링
    title = []
    url = []
    date = []
    for i in range(len(keyword_list)) :
        keyword = keyword_list[i]
        url_keyword = "https://platum.kr//?s=" + keyword

        soup = requests.get(url_keyword).text
        html = BeautifulSoup(soup, 'html.parser')
    
    # 키워드당 n개 기사
        for j in range(n) : 
            title.append(html.find_all('h5')[j].find('a')['title'])
            url.append(html.find_all('h5')[j].find('a')['href'])
            date.append(html.find_all('span', {"class" : "post_info_date"})[j].find('a').text)

    # 연결 상태 확인
    data = {'payload': '{"text": title }'}
    webhook_url = "https://hooks.slack.com/services/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"
    response = requests.post(webhook_url, data=data)

    content = []
    for i in range(len(title)) : 
        content.append({"title": title[i], "url":url[i], "date": date[i]})

    # 중복제거
    re_content = list(map(dict, set(tuple(sorted(d.items())) for d in content))) 

    # 최근 N일 기준
    for i in range(len(re_content)) :
        re_content[i]["re_date"] = re_content[i]["date"][10:]
        re_content[i]["re_date"] = datetime.datetime.strptime(re_content[i]["re_date"],'%Y/%m/%d')

    content = re_content
    now = datetime.datetime.now()
    period = now - datetime.timedelta(days=days)

    num = []
    for i in range(len(content)) : 
        if period < content[i]["re_date"] :
            num.append(i)

    # html 마크다운 설정
    temp = []
    for i in num : 
        if i == num[-1] : 
            temp.append("> " + content[i]['title'] + "\n> " + content[i]['url'] + " \n> " + content[i]['date'])
        else : 
            temp.append("> " + content[i]['title'] + "\n> " + content[i]['url'] + " \n> " + content[i]['date'] + "\n\n")
    temp
    content = "".join(temp)

    # 슬랙 전송
    payload= {"text": content }
    requests.post(webhook_url, data=json.dumps(payload), headers={'Content-Type':'application/json'})

keyword_list = ["헬스","금융"]
getNews(keyword_list, 60, 3)

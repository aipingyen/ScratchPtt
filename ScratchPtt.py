import requests
from bs4 import BeautifulSoup
import re
import time
import arrow

HOST = "https://www.ptt.cc"
boardName = "Gossiping"
index = HOST + "/bbs/" + boardName + "/index.html"
headers = {'cookie': 'over18=1;'}


def getPages(number):
    global HOST, index, headers
    r = requests.get(index, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    link = HOST + soup.select("a.wide")[1]['href']
    match = re.match(r'(.*index)(\d+)(.html)', link)
    lastPage = int(match.group(2)) + 1

    pageList = []
    for i in range((lastPage - number + 1), (lastPage + 1)):
        page = match.group(1) + str(i) + match.group(3)
        pageList.append(page)

    return pageList


def getPosts(pageUrl):
    global headers
    r = requests.get(pageUrl, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    postList = []
    links = soup.select("div.title > a")
    for link in links:
        title = link.text
        href = HOST + link['href']
        postList.append(href)
    return postList

#not need strings
exclude = ['','--']

#not need string's beginning
excludeB = ['※ 引述',':']

#using 'year</span></div>' to split the article
years = []
thisYear = time.localtime(time.time()).tm_year
for year in range(2005, thisYear+1):
    years.insert(0, str(year))

def getText(postUrl):
    global boardName, headers, exclude, excludeB, years
    dic = {}
    r = requests.get(postUrl, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    info = soup.select(".article-meta-value")

    #split name and nickName
    match = re.match(r'(.*)\s\((.*)\)', info[0].text)
    name = match.group(1)
    nickName = match.group(2)
    title = info[2].text
    postTime = info[3].text
    atime = arrow.Arrow.strptime(postTime, '%a %b %d %H:%M:%S %Y' ,tzinfo='Asia/Taipei')

    #get text
    text = repr(r.text)
    match = re.match(r'(.*)[%s]</span></div>(.*)<span class="f2">※ 發信站: 批踢踢實業坊(.*)' % "|".join(years), text)
    strings = []
    if match:
        strings = match.group(2).split(r"\n")

    #clean text
    reStrings = []
    for string in strings:
        match2 = re.match(r'.*(<.*>).*', string)
        while match2:
            string = string.replace(match2.group(1), '')
            match2 = re.match(r'.*(<.*>).*', string)
        if string not in exclude:
            if not re.match('[%s].*' % "|".join(excludeB), string):
                reStrings.append(string)


    #get pushs
    pushs = soup.select("div.push")
    articles = []
    for push in pushs:
        tag = push.select_one(".push-tag").text.strip()
        userid = push.select_one(".push-userid").text
        content = push.select_one(".push-content").text.replace(": ", "")
        ipdatetime = push.select_one(".push-ipdatetime").text.strip()
        article = {}
        article['tag'] = tag
        article['userid'] = userid
        article['content'] = content
        article['ipdatetime'] = ipdatetime
        articles.append(article)

    dic['name'] = name
    dic['nickName'] = nickName
    dic['title'] = title
    dic['postTime'] = atime
    dic['contents'] = reStrings
    dic['articles'] = articles
    return dic
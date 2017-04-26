import requests
from bs4 import BeautifulSoup
import re
import time

HOST = "https://www.ptt.cc"
boardName = "Gossiping"
index = HOST + "/bbs/" + boardName + "/index.html"
headers = {'cookie': 'over18=1;'}


def getPages(number):
    global HOST, index, headers
    r = requests.get(index, headers=headers)
    soup = BeautifulSoup(r.content, "lxml")
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
    soup = BeautifulSoup(r.content, "lxml")
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
    global headers, exclude, excludeB, years
    r = requests.get(postUrl, headers=headers)
    text = repr(r.text)
    match = re.match(r'(.*)[%s]</span></div>(.*)<span class="f2">※ 發信站: 批踢踢實業坊(.*)' % "|".join(years), text)
    if match:
        strings = match.group(2).split(r"\n")

    reStrings = []
    for string in strings:
        match2 = re.match(r'.*(<.*>).*', string)
        while match2:
            string = string.replace(match2.group(1), '')
            match2 = re.match(r'.*(<.*>).*', string)
        if string not in exclude:
            if not re.match('[%s].*' % "|".join(excludeB), string):
                reStrings.append(string)
    return reStrings

def artInfo(postUrl):
    data = []
    name = None
    nickName = None
    board = None
    title = None
    time = None

    r = requests.get(postUrl, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    info = soup.select(".article-meta-value")

    match = re.match(r'(\w+)(\s\((.*)\))?', info[0].text)
    if match:
        name = match.group(1)
        nickName = match.group(3)
    board = info[1].text
    title = info[2].text
    time = info[3].text

    data.append(name)
    data.append(nickName)
    data.append(board)
    data.append(title)
    data.append(time)
    return data

import requests
from bs4 import BeautifulSoup
import re
import time
import jieba
from collections import Counter
from dateutil import parser

HOST = "https://www.ptt.cc"
boardName = "Gossiping"
index = HOST + "/bbs/" + boardName + "/index.html"
headers = {'cookie': 'over18=1;'}


def getPages(number):
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
    name = None
    nickName = None
    title = None
    dtime = None
    dic = {}
    r = requests.get(postUrl, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    info = soup.select(".article-meta-value")
    try:
        #split name and nickName
        match = re.match(r'(.*)\s\((.*)\)', info[0].text)
        if match:
            name = match.group(1)
            nickName = match.group(2)
        else:
            with open('notmatchError.txt', 'a') as f:
                f.write(postUrl)
                f.write('\n')
        title = info[2].text
        postTime = info[3].text
        # atime = arrow.Arrow.strptime(postTime, '%a %b %d %H:%M:%S %Y' ,tzinfo='Asia/Taipei').timestamp
        dtime = parser.parse(postTime)
        # dtime = dtime.__str__()
    except IndexError:
        with open('IndexError.txt', 'a') as f:
            f.write(postUrl)
            f.write('\n')

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
    p_good = 0
    p_bad = 0
    p_balance = 0
    for push in pushs:
        userid = None
        content = None
        ipdatetime = None
        try:
            tag = push.select_one(".push-tag").text.strip()
            userid = push.select_one(".push-userid").text
            content = push.select_one(".push-content").text.replace(": ", "")
            ipdatetime = push.select_one(".push-ipdatetime").text.strip()
        except AttributeError:
            with open('AttributeError.txt', 'a') as f:
                f.write(postUrl)
                f.write('\n')
        article = {}
        article['tag'] = tag
        if tag == '推':
            p_good += 1
        elif tag == '噓':
            p_bad += 1
        else:
            p_balance += 1
        article['userid'] = userid
        article['content'] = content
        article['ipdatetime'] = ipdatetime
        articles.append(article)

    dic['name'] = name
    dic['nickName'] = nickName
    dic['title'] = title
    dic['postTime'] = dtime
    dic['contents'] = reStrings
    dic['articles'] = articles
    #level is good pushs minus bad pushs
    level = p_good - p_bad
    dic['level'] = level
    #consider the post is good or bad or contentious
    type = None
    if p_good != 0 or p_bad != 0:
        if p_good - p_bad == p_good:
            type = 'good'
        elif p_bad - p_good == p_bad:
            type = 'bad'
        else:
            if p_good / p_bad >= 1.3:
                type = 'good'
            elif p_good/ p_bad <= 0.7:
                type = 'bad'
            else:
                type = 'contentious'
    dic['type'] = type
    return dic

#import strings array into useJieba, return list of popular words
def useJieba(strings):
    words = Counter()
    for string in strings:
        cutString = jieba.cut(string)
        for word in cutString:
            if word in words:
                words[word] += 1
            else:
                words[word] = 1
    words = words.most_common()
    c_words= []
    for word in words:
        if len(word[0]) != 1 and word[1] > 1:
            c_words.append(word[0])
            if len(c_words) > 9:
                break
    return c_words

def getArtWords(articles):
    arts = []
    for art in articles:
        string = art['content']
        arts.append(string)
    artWords = useJieba(arts)
    return artWords

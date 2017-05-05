import ScratchPtt
import sqlalchemy
from sqlalchemy import create_engine
import pandas as pd
import threading

lowest = 0
df = pd.DataFrame()

class mythread(threading.Thread):
    def __init__(self, posts, lock):
        threading.Thread.__init__(self)
        self.posts = posts
        self.lock = lock
    def run(self):
        global df
        dfp = getdfp(self.posts)
        self.lock.acquire()
        df = df.append(dfp)
        self.lock.release()

def main():
    global df
    pages = ScratchPtt.getPages(2)
    threads = []
    for page in pages:
        posts = ScratchPtt.getPosts(page)
        lock = threading.Lock()
        thread = mythread(posts, lock)
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    engine = create_engine('sqlite:///ptt.sqlite3')
    df.to_sql('gosp',
              engine,
              if_exists='replace',
              index=False,
              dtype={'name': sqlalchemy.types.VARCHAR(20),
                    'nickName': sqlalchemy.types.VARCHAR(20),
                    'title': sqlalchemy.types.VARCHAR(50),
                    'postTime': sqlalchemy.types.DateTime,
                    'level': sqlalchemy.types.INT,
                    'type': sqlalchemy.types.VARCHAR(10)})

def getdfp(posts):
    dfp = pd.DataFrame()
    for post in posts:
        text = ScratchPtt.getText(post)
        name = text['name']
        nickName = text['nickName']
        title = text['title']
        postTime = text['postTime']
        level = text['level']
        type = text['type']
        # conWords = ScratchPtt.useJieba(text['contents'])
        # artWords = ScratchPtt.getArtWords(text['articles'])
        if level != 1:
            dfx = pd.DataFrame([{"name":name,
                                "nickName":nickName,
                                "title":title,
                                "postTime":postTime,
                                "level":level,
                                "type":type,}])
            dfp = dfp.append(dfx)
    return dfp


def read_sql():
    df = pd.read_sql("select * from gosp;", create_engine('sqlite:///ptt.sqlite3'))
    return df

main()
print(read_sql())

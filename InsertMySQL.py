import ScratchPtt
import pymysql

text = ScratchPtt.getText("https://www.ptt.cc/bbs/Gossiping/M.1493555015.A.C84.html")
name = text['name']
nickName = text['nickName']
title = text['title']
postTime = text['postTime']
level = text['level']
type = text['type']
conWords = ScratchPtt.useJieba(text['contents'])
artWords = ScratchPtt.getArtWords(text['articles'])

db = pymysql.connect("localhost", "root", "root", "testdb", charset="utf8")
cursor = db.cursor()
sql = """INSERT INTO ptt VALUES('%s','%s','%s','%s','%s','%s')""" % (name, nickName, title, postTime, level, type)
cursor.execute(sql)
db.commit()
db.close()
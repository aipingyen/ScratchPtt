import ScratchPtt
import threading


class mythread(threading.Thread):
    def __init__(self, post):
        threading.Thread.__init__(self)
        self.post = post
    def run(self):
        text = ScratchPtt.getText(post)
        print(text['title'])

pages = ScratchPtt.getPages(5)
for page in pages:
    posts = ScratchPtt.getPosts(page)
    for post in posts:
        threadx = mythread(post)
        threadx.start()


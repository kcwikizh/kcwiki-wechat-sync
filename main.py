# -*- coding: UTF-8 -*-

import feedparser
from bs4 import BeautifulSoup
import requests
import lxml
import re
import pywikibot
from pywikibot.specialbots import UploadRobot
import time
from config import *
from qiniu_pics import qiniu_upload

template_homepage = "<includeonly>\n<div style=\"width:100%\">\n{{{{Panel\n|pic    = {pic}\n|title  = {title}\n|tag    = 文/{author}\n|link   = {link}\n}}}}\n</div>\n</includeonly>"
site = pywikibot.Site('zh', 'kcwiki')
page = pywikibot.Page(site, "Template:首页轮播")


header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
pattern = r'var msg_cdn_url\s*=\s*\"(.*)\"'
feed = feedparser.parse(biz_rss_url)

articles = [
    {
        "title": feed.entries[0].title,
        "link": feed.entries[0].link,
        "author": feed.entries[0].author
    },
    {
        "title": feed.entries[1].title,
        "link": feed.entries[1].link,
        "author": feed.entries[1].author
    }
]

count = 0
for i in range(0, len(articles)-1):
    web = requests.get(articles[i]["link"], headers=header)
    soup = BeautifulSoup(web.text, 'lxml')
    js = soup.find_all("script")
    for each in js:
        match = re.search(pattern, str(each), flags=re.M|re.I)
        if match is not None:
            articles[i]["cover"] = match.groups()[0]
            print(match.groups()[0])
            pic = requests.get(match.groups()[0], headers=header)
            with open("pic.jpeg", 'wb') as f:
                f.write(pic.content)
            local_file = 'pic.jpeg'
            key = "{}.jpeg".format(int(time.time()))

            pic_cropped = qiniu_upload(local_file, key)
            with open("{}".format(key), 'wb') as f:
                f.write(pic.content)

            uploadbot = UploadRobot(url=[key], description="Biz article cover uploaded by bot", keepFilename=True,
                                    verifyDescription=False, ignoreWarning=True)
            uploadbot.run()
            articles[i]["cover"] = key
page.text = template_homepage.format(pic=articles[0]["cover"], link=articles[0]["link"], title=articles[0]["title"],
                                     author=articles[0]["author"])
page.save("biz update")

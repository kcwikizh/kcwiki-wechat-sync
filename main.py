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
import json
import os

template_homepage = "<includeonly>\n<div style=\"width:100%\">\n{{{{Panel\n|pic    = {pic}\n|title  = {title}\n|tag    = 文/{author}\n|link   = {link}\n}}}}\n</div>\n</includeonly>"
site = pywikibot.Site('zh', 'kcwiki')
page = pywikibot.Page(site, "Template:首页轮播")


header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
pattern = r'var msg_cdn_url\s*=\s*\"(.*)\"'


def update_article(article):
    web = requests.get(article["link"], headers=header)
    soup = BeautifulSoup(web.text, 'lxml')
    js = soup.find_all("script")
    for each in js:
        match = re.search(pattern, str(each), flags=re.M | re.I)
        if match is not None:
            article["cover"] = match.groups()[0]
            print(match.groups()[0])
            pic = requests.get(match.groups()[0], headers=header)
            with open("pic.jpeg", 'wb') as f:
                f.write(pic.content)
            local_file = 'pic.jpeg'
            key = "{}.jpeg".format(int(time.time()))

            pic_cropped = qiniu_upload(local_file, key)
            with open("{}".format(key), 'wb') as f:
                f.write(pic_cropped)

            uploadbot = UploadRobot(url=[key], description="Biz article cover uploaded by bot", keepFilename=True,
                                        verifyDescription=False, ignoreWarning=True)
            uploadbot.run()
            article["cover"] = key

    page.text = template_homepage.format(pic=article["cover"], link=article["link"], title=article["title"],
                                         author=article["author"])

    page.save("biz update")
    with open('lastupdated.json', 'w') as f:
        f.write(json.dumps(article, ensure_ascii=False))


if __name__ == "__main__":
    feed = feedparser.parse(biz_rss_url)
    articles = []

    for item in feed.entries:
        dic = dict()
        dic["title"] = item["title"]
        dic["link"] = item["link"]
        dic["author"] = item["author"]
        dic["update"] = time.mktime(time.strptime(item["published"], "%a, %d %b %Y %H:%M:%S %Z"))
        articles.append(dic)

    if os.path.exists('lastupdated.json'):
        with open('lastupdated.json', 'r') as f:
            lastupdated = json.load(fp=f)
    else:
        lastupdated = None

    if lastupdated is None:
        for article in articles:
            if "百科娘说两句" in article["title"] or "小说" in article["title"]:
                continue

            update_article(article)
            break
    else:
        for article in articles:
            if article["title"] == lastupdated["title"] and article["update"] == lastupdated["update"]:
                continue
            elif "百科娘说两句" in article["title"]:
                continue
            elif lastupdated["update"] - article["update"] < 86400 or article["update"] > lastupdated["update"]:
                update_article(article)
                break



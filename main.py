import feedparser
from bs4 import BeautifulSoup
import requests
import lxml
import re
import pywikibot

template_homepage = "<includeonly>\n<div style=\"width:100%\">\n{{{{Panel\n|pic    = {pic1}\n|title  = {title1}\n|tag    = 文/{author1}\n|link   = {link1}\n}}}}\n</div>\n</includeonly>"
site = pywikibot.Site('zh', 'kcwiki')
page = pywikibot.Page(site, "Template:镇守府沙滩")

print(page.text)
proxy = {"http": "http://home.yuudachi.moe:4411",
         "https": "http://home.yuudachi.moe:4411"}

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
pattern = r'var msg_cdn_url\s*=\s*\"(.*)\"'
feed = feedparser.parse("https://cdn.werss.weapp.design/api/v1/feeds/a6d272dc-e349-4117-a0c8-a3c79b2a8120.xml")

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
    web = requests.get(articles[i]["link"], headers=header, proxies=proxy)
    soup = BeautifulSoup(web.text, 'lxml')
    js = soup.find_all("script")
    for each in js:
        match = re.search(pattern, str(each), flags=re.M|re.I)
        if match is not None:
            articles[i]["cover"] = match.groups()[0]
page.text = template_homepage.format(pic1=articles[0]["cover"], link1=articles[0]["link"], title1=articles[0]["title"],
                               author1=articles[0]["author"])


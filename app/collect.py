# coding=utf-8

import re
import requests as rq

addr_head = "http://so.gushiwen.org/view_"
addr_tail = ".aspx"


def get_article(page_content):
    re_remove = re.compile("<.*/>")
    re_lineseq = re.compile("。")
    article = {}
    result = re.search(r'.*<h1>(.*)</h1>.*', page_content)
    article["title"] = (re_remove.sub("", str(result.groups()[0]))).decode("utf-8").encode("gbk", "ignore")
    result = re.search(r'.*朝代.*>(.*)</p>.*', page_content)
    article["dynasty"] = re_remove.sub("", str(result.groups()[0])).decode("utf-8").encode("gbk", "ignore")
    result = re.search(r'.*作者.*k">(.*)</a>.*', page_content)
    article["author"] = re_remove.sub("", str(result.groups()[0])).decode("utf-8").encode("gbk", "ignore")
    result = re.search(r'.*>原文.*</p>\s*(.*\n*.*)\s*</div>', page_content)
    if result is None:
            result = re.search(r'.*>原文.*</p>\s*(.*\s*<br/>\s*.*)\s*.*</div>', page_content)
    article["body"] = re_lineseq.sub("。\n", re_remove.sub("", str(result.groups()[0]))).decode("utf-8").encode("gbk",
                                                                                                               "ignore")
    return article


def start_spider(index):
    addr = addr_head+index+addr_tail
    r = rq.get(addr)
    return get_article(r.content)


def parse_search_result(result):
    clue = re.findall(r'.*href="/view_(\d*).*', result)
    articles = []
    for index in clue:
        articles.append(start_spider(index))
    return articles

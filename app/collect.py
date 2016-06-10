# coding=utf-8

import re
import os
import requests as rq
from app.models import  Prototype
import bleach

addr_head = "http://so.gushiwen.org/view_"
addr_tail = ".aspx"


def get_article(page_content):
    re_remove = re.compile("</*\s*p\s*>|<\s*br\s*/*>|&.*;|\s*")
    re_remove_tag = re.compile("<div.*/div>|\(.{1,20}\)")
    re_linesep = re.compile("。")
    article = {}
    try:
        result = re.search(r'.*<h1>(.*)</h1>.*', page_content)
        article["title"] = (re_remove.sub("", str(result.groups()[0])))
        result = re.search(r'.*朝代.*>(.*)</p>.*', page_content)
        article["dynasty"] = re_remove.sub("", str(result.groups()[0]))
        result = re.search(r'.*作者.*k">(.*)</a>.*', page_content)
        article["author"] = re_remove.sub("", str(result.groups()[0]))
        result = re.search(r'.*>原文.*</p>\s*(.*\n*.*)\s*</div>', page_content)
        if result is None:
            result = re.search(r'.*>原文.*</p>\s*(.*\s*<br/>\s*.*)\s*.*</div>', page_content)
        article["body"] = re_remove_tag.sub("", re_remove.sub("", str(result.groups()[0])))\
            .strip()
    except AttributeError:
        return None
    if Prototype.add_prototype(article["title"], article["dynasty"], article["author"], article["body"]) is False:
        return None
    article["body"] = re_linesep.sub("。<br/>", article["body"])
    return article


def start_spider(index):
    addr = addr_head + index + addr_tail
    r = rq.get(addr)
    return get_article(r.content)


def parse_search_result(result):
    clue = re.findall(r'.*href="/view_(\d*).*', result)
    articles = []
    f = open("f:/result_search.txt", "a+")
    for index in clue:
        article = start_spider(index)
        if article is not None:
            articles.append(article)
        else:
            f.write(index + os.linesep)
    f.close()
    return articles

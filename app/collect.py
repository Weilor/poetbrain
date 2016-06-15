# coding=utf-8

import re
import os
import requests as rq
from app.models import Prototype
import bleach

addr_head = "http://so.gushiwen.org/view_"
addr_tail = ".aspx"


def get_article(page_content):
    """
    这是爬虫解析的主体，爬取下来的网页中，这里主要关注诗歌古文的朝代、作者以及原文，通过正则匹配相关的字符串并存储。
    由于这个古诗文网站写的比较奇葩，原文附近的字符串不是一模一样的，而如果选择了宽泛的表达式，有导致正确率降低，因此
    这里做了两次提取。这部分很尴尬，以后技术提升后进行重构。
    :param page_content 爬取下来的网页内容，字符串形式
    """
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
        article["body"] = re_remove_tag.sub("", re_remove.sub("", str(result.groups()[0]))) \
            .strip()
    except AttributeError:
        return None
    if Prototype.add_prototype(article["title"], article["dynasty"], article["author"], article["body"]) is False:
        return None
    article["body"] = re_linesep.sub("。<br/>", article["body"])
    return article


def start_spider(index):
    if isinstance(index, type("")):
        index = str(index)
    addr = addr_head + index + addr_tail
    print index
    r = rq.get(addr)
    return get_article(r.content)


def parse_search_result(c_app, result):
    with c_app.app_context():
        clue = re.findall(r'.*href="/view_(\d*).*', result)
        print clue.__repr__()
        articles = []
        for index in clue:
            print index
            article = start_spider(index)
            if article is not None:
                articles.append(article)
        return articles

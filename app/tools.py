# coding=utf-8

import requests
import re
from app.models import Prototype
from app import collect
from threading import Thread


def get_article_from_search(c_app, address):
    """从搜索页面结果中遍历所有“下一页”链接并得到当前页中所有的古诗文页面链接，使用子线程爬取古诗文
    :param c_app:为取得当前app的上下文而传入的app实例
    :param address:搜索页地址,string类型
    """
    with c_app.app_context():
        print address
        page_content = requests.get(address).content
        while page_content is not None:
            thr = Thread(target=collect.parse_search_result, args=[c_app, page_content])
            thr.start()
            print thr.__repr__()
            result = re.search('href="(.*)">下一页', page_content)
            if result is not None:
                page_content = requests.get("http://so.gushiwen.org" + result.groups()[0]).content
            else:
                break
        return


def get_article_from_db(author_or_title):
    """
    按照作者或者题目作为索引从db中得到article记录
    :param author_or_title:string type
    """
    articles = Prototype.is_prototype_exist(author_or_title)
    return articles


def encode_string_dict(string_dict):
    """中文储存及显示问题，需要转换编码格式
    :param string_dict:字符串字典
    """
    for key in string_dict.keys():
        string_dict[key] = string_dict[key].decode("utf-8").encode("gbk", "ignore")
    return string_dict


def put_linesep_in(string_body):
    put_linesep = re.compile(u"。")
    string_body = put_linesep.sub(u"。<br/>", string_body)
    return string_body


def check_memento(prototype_text, form_text):
    len_prototype = len(prototype_text)
    len_form = len(form_text)
    len_loop = min((len_prototype, len_form))
    incorrect_list = []
    for i in range(len_loop):
        if prototype_text[i] != form_text[i]:
            incorrect_list.append(i)
    incorrect_count = len(incorrect_list)
    while 0 != len(incorrect_list):
        form_text = string_insert(form_text, incorrect_list.pop(), "<del>", "</del>")
        print form_text
    return form_text, incorrect_count


def string_insert(origin_string, index, pre_sub_string, post_sub_string):
    """在指定字符串的指定字符前后插入字符,在字符串origin_string[index]的前后分别插入pre_sub_string,post_string
    :param origin_string,需要被处理的字符串
    :param index,在字符串origin_string[index]的前后插入
    :param pre_sub_string,插入前缀
    :param post_sub_string:插入后缀
    """
    if index == 0:
        pre_origin = ""
    elif index == (len(origin_string) - 1):
        post_orgin = ""
    elif 0 < index < (len(origin_string) - 1):
        pre_origin = origin_string[:index]
        post_orgin = origin_string[index + 1:]
    else:
        return None
    return pre_origin + pre_sub_string + origin_string[index] + post_sub_string + post_orgin


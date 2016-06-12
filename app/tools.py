# coding=utf-8

import requests
import re
from app.models import Prototype
from app import collect
from threading import Thread


def get_article_from_search(c_app, address):
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
    articles = Prototype.is_prototype_exist(author_or_title)
    return articles


def encode_string_dict(string_dict):
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


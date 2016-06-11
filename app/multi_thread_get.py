# coding = utf-8
import collect
from threading import Thread


def multi_thread_get_article():
    for i in range(10):
        thr = Thread(target=collect.start_spider, args=[i])
        thr.start()
    return

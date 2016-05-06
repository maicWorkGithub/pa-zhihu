#!/usr/bin/env python3
# coding: utf-8

from gevent import monkey
monkey.patch_all()
import gevent
import sys

# todo: fetchall() 为啥执行第二次就丢失了返回值

'''
1, 开十个线程,
2, 给参数, 打印相应的结果:(这个在let's go里)
    - 一个网址,给出这个人的dict
    - 'time', 给出运行时间
    - 'peoples', 给出抓到的人数
    - 'efficiency', 给出抓到的人数 除以 运行时间
    - 'links crawled', 给出已经抓过的链接数
    - 'links non-crawled', 给出剩余的链接数
    - 'all links', 给出所有链接数
    - ''

'''

def gevent_task(fn, sleep=1, work_count=10):
    works = []
    for i in range(work_count):
        works.append(gevent.spawn(fn, ))







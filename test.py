#!/usr/bin/env python3
# coding: utf-8
from lxml import html
import json
from urllib.parse import urlencode
import re


def _get_attr_str(arr):
    if len(arr):
        return arr[0]
    else:
        return ''


person_dict = {}
with open('evanyou.html', 'rb') as f:
    file_content = f.read()

html_ll = html.fromstring(file_content)
# print(pattern.findall(str(file_content)))
# print(json.dumps(person_dict, sort_keys=True, indent=4))
# print(json.loads(html_ll.xpath(u'//div[@class="zh-general-list clearfix"]/@data-init')[0])['params']['hash_id'])

data = {'method': 'next',
        '_xsrf': '25b36ac4d2d64b1242bf0150485d0b33'
        }

params = {
    'order_by': 'created',
    'offset': 20,
    'hash_id': 'cfdec6226ece879d2571fbc274372e9f'
}

data['params'] = re.sub("(?<=:) *", "", json.dumps(params))

print(json.dumps(params).replace(' ', ''))

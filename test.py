#!/usr/bin/env python3
# coding: utf-8
from lxml import html
from lxml.html import tostring

with open('evanyou.html', 'rb') as f:
    file_content = f.read()
    html_content = html.fromstring(file_content)
    left_profile = html_content.xpath(u'//div[@class="zu-main-content-inner"]')

    username = left_profile[0].xpath(u'//div[@class="zm-profile-header-main"]//span[@class="name"]/text()')
    gender = left_profile[0].xpath(u'//span[@class="item gender"]/i/@class')
    location = left_profile[0].xpath(u'//span[@class="location item"]/@title')

    print(tostring(left_profile[0]))
    print(username, gender, location)
    print(html_content.xpath(u'//a[@class="name"]/text()'))

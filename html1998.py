#!/usr/bin/python
# coding=utf-8

__license__ = 'GPL 3'
__copyright__ = '2011, Tomasz Długosz <tomek3d@gmail.com>'

import re
import urllib2
from lxml import html

def resolveAbbr(text):

    return text

def ToC():
    url='http://biblia.deon.pl/PS/Ps_ksiegi.html'
    response = urllib2.urlopen(url).read()
    doc = html.fromstring(response)
    for data in doc.xpath('//td[@width="50%"]/table'):
        print "Testament"
        testament= []
        for data in data.xpath('.//tr/td/font/b'):
            bookName=''.join(data.xpath('.//a/text()')).strip()
            bookLink=''.join(data.xpath('.//a/@href')).replace('/Nazwa0.html','')
            testament.append((bookName,bookLink))
        for bn, bl in testament:
            print bn, bl


ToC()

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
        for data in data.xpath('.//tr/td/font/b'):
            print ''.join(data.xpath('.//a/text()'))
            print ''.join(data.xpath('.//a/@href'))


ToC()

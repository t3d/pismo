#!/usr/bin/python
# coding=utf-8

__license__ = 'GPL 3'
__copyright__ = '2011, Tomasz Długosz <tomek3d@gmail.com>'

import urllib2
from lxml import html

masterURL='http://biblia.deon.pl/PS/'

def ToC():
    url = masterURL+'Ps_ksiegi.html'
    response = urllib2.urlopen(url).read()
    doc = html.fromstring(response)
    newTes = oldTes = []
    for data in doc.xpath('//td[@width="50%"]/table'):
        testament= []
        for idata in data.xpath('.//tr/td/font/b'):
            bookName=''.join(idata.xpath('.//a/text()')).strip()
            bookLink=''.join(idata.xpath('.//a/@href')).replace('/Nazwa0.html','')
            testament.append((bookName,bookLink))
        if oldTes == []:
            oldTes = list(testament)
        else:
            newTes = list(testament)
    return (oldTes, newTes)

def bookContent(bl):
    url = masterURL+bl+'/ROZDZ.HTM'
    response = urllib2.urlopen(url).read()
    doc = html.fromstring(response)
    chapters =[]
    for data in doc.xpath('//table/tr'):
        id = ''.join(data.xpath('.//td/font/b/a/@href'))
        if not id:
            continue
        name = ''.join(data.xpath('.//td/font/b/a/text()'))
#print name, re.sub('javascript\:LoadTW\(\ \'','',id)
        chapters.append(( name, id.split('\'')[1]+'T.HTM' if 'javascript' in id else id))
    return chapters

#stary,nowy = ToC()
#for bn, bl in stary:
#    print bn, bl
#for bn, bl in nowy:
#    print bn, bl
bookContent('10_2SM_')


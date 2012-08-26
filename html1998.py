#!/usr/bin/python
# coding=utf-8

__license__ = 'GPL 3'
__copyright__ = '2012, Tomasz Długosz <tomek3d@gmail.com>'

import tempfile
import urllib2
from lxml import html
from lxml.html.clean import clean_html
import shutil
import os
import re

masterURL='http://biblia.deon.pl/PS/'
tmpdir = tempfile.mkdtemp()

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

xhtmlHeader = '''<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="application/xhtml+xml; charset=utf-8" />
<link rel="stylesheet" type="text/css" href="/style.css" />
<title>'''

replaceStrings = (
    ('&#13;', ''),
    ('&#160;', '&nbsp;'),
    ('&#171;', '«'),
    ('&#187;', '»'),
    ('&#261;', 'ą'),
    ('&#260;', 'Ą'),
    ('&#263;', 'ć'),
    ('&#262;', 'Ć'),
    ('&#281;', 'ę'),
    ('&#280;', 'Ę'),
    ('&#322;', 'ł'),
    ('&#321;', 'Ł'),
    ('&#324;', 'ń'),
    ('&#323;', 'Ń'),
    ('&#243;', 'ó'),
    ('&#211;', 'Ó'),
    ('&#347;', 'ś'),
    ('&#346;', 'Ś'),
    ('&#380;', 'ż'),
    ('&#379;', 'Ż'),
    ('&#378;', 'ź'),
    ('&#377;', 'Ź'),
    (' target="Dolna"', '')
)

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
        chapters.append(( name, id.split('\'')[1]+'T.HTM' if 'javascript' in id else id))
    return chapters

def saveChapter(bookLink, chapterLink):
    url = 'http://biblia.deon.pl/PS/' + bookLink + '/' + chapterLink
    response = urllib2.urlopen(url).read()
    doc = html.fromstring(response)
    start = 77 if 'T' in chapterLink.split('.')[0] else 114
    content = html.tostring(clean_html(doc))[start:-6]
    for fromPattern, toPattern in replaceStrings:
        content = re.sub(fromPattern, toPattern, content)
    #print content
    filename = bookLink + re.sub('HTM', 'xhtml', chapterLink)
    chapterfile = open(filename, 'w')
    chapterfile.write(xhtmlHeader + chapterLink.split('.')[0] + '</title></head>' + content + '</html>')
    chapterfile.close()

def saveIndex(index):
    print 'generating INDEX...'
    chapterfile = open('index.html', 'w')
    chapterfile.write('<!DOCTYPE html><html><body>')
    for bookLink, chapterName, chapterLink in index:
        chapterfile.write('<a href=\"' + bookLink + re.sub('HTM', 'xhtml', chapterLink) + '">' + chapterName.encode('utf-8') + '</a><br>')
    chapterfile.write('</body></html>')
    chapterfile.close()

def getBook(index,bn,bl):
    print 'working on ' + bn + '...'
    for chapterName,chapterLink in bookContent(bl):
        #print chapterName, chapterLink
        saveChapter(bl,chapterLink)
        index.append((bl,chapterName,chapterLink))

def epubBuild():
    print tmpdir
    os.mkdir(os.path.join(tmpdir,'META-INF'))
    #os.mkdir(os.path.join(tmpdir,'content'))
    file = open(os.path.join(tmpdir,'mimetype'), 'w')
    print>>file, 'application/epub+zip'
    file.close()

#epubBuild()
stary,nowy = ToC()
index =[]
for bn, bl in stary:
    #print bn, bl
    getBook(index,bn,bl)
for bn, bl in nowy:
    #print bn, bl
    getBook(index,bn,bl)
#getBook(index,'2 Ks. Samuela', '10_2SM_')
#saveChapter('10_2SM_', '014T.HTM')
saveIndex(index)

shutil.rmtree(tmpdir)

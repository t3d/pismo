#!/usr/bin/python
# coding=utf-8

__license__ = 'GPL 3'
__copyright__ = '2012-2014, Tomasz Długosz <tomek3d@gmail.com>'

import urllib2
from lxml import html
from lxml.html.clean import clean_html
import re

masterURL='http://biblia.deon.pl/'

def getPage(url):
    fetcher = urllib2.build_opener()
    fetcher.addheaders = [('User-agent', 'Mozilla/5.0')]
    response = fetcher.open(url)
    return html.fromstring(response.read())

def ToC():
    doc = getPage(masterURL)
    newTes = oldTes = []
    bookNumber = 0
    bookShort = ''
    for data in doc.xpath('//select[@id="ksiega"]/option'):
        bookNumber=''.join(data.xpath('./@value'))
        bookShort=''.join(data.xpath('./text()')).replace(' ','')
        if int(bookNumber) < 47 :
            oldTes.append((bookNumber,bookShort))
        else:
            newTes.append((bookNumber,bookShort))
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
    ('</font></font></center>', '</span>'),
    ('</font>', ''),
    ('</b></font></p>', '</span>'),
    ('</b>', '</span>'),
    (r'(</p>)+<span', '<span'),
    (r'</span></p>', '</span>'),
    ('<br></p></font>', '</p>'),
    (r'<a name="0*', '<a id="w'),
    ('<br>', '<br/>')
)

def bookContent(booknumber):
    url = masterURL + 'ksiega.php?id=' + booknumber
    doc = getPage(url)
    chapters =[]
    for data in doc.xpath('//select[@name="rozdzial"]/option'):
        bookNumber=''.join(data.xpath('./@value'))
        chapters.append(bookNumber)
    return chapters

def saveChapter(chapterNumber,chapterFile):
    url = masterURL + 'rozdzial.php?id=' + chapterNumber
    doc = getPage(url)
    content=html.tostring(doc.xpath('.//div[@class="tresc"]')[0])
    footnotes=doc.xpath('.//div[@class="footnotes-content"]')
    for fromPattern, toPattern in replaceStrings:
        content = re.sub(fromPattern, toPattern, content)
    print content
    file = open(chapterFile, 'w')
    file.write(xhtmlHeader + str(chapterNumber) + '</title></head><body>' + content + '</body></html>')
    file.close()

def saveIndex(index):
    print 'generating INDEX...'
    chapterfile = open('index.html', 'w')
    chapterfile.write('<!DOCTYPE html><html><body>')
    for bookLink, chapterName, chapterLink in index:
        chapterfile.write('<a href=\"' + bookLink + re.sub('HTM', 'xhtml', chapterLink) + '">' + chapterName.encode('utf-8') + '</a><br>')
    chapterfile.write('</body></html>')
    chapterfile.close()

def getBook(index,bn,bs):
    print 'working on book number ' + bn + '...'
    for chapterNumber in bookContent(bn):
        print chapterNumber
        chapterFile = str(chapterNumber) + '.xhtml'
        saveChapter(chapterNumber,chapterFile)
        #index.append((bl,chapterName,chapterLink))

stary,nowy = ToC()
index =[]
for bn, bl in stary:
    #print bn, bl
    getBook(index,bn,bl)
for bn, bl in nowy:
    #print bn, bl
    getBook(index,bn,bl)
#getBook(index,'2 Ks. Samuela', '10_2SM_')
#saveChapter('10_2SM_', '001T.HTM', '2 Ks. Samuela')
#saveChapter('10_2SM_', '014T.HTM', '2 Ks. Samuela')
saveIndex(index)

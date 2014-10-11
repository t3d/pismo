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
    (r'<font size="4" color="#0000FF"><b>(\d+)</b></font>', r'<span class="numer">\1</span>'),
    (r'<font color="#FF0000"><b>(.*?)</a></b></font>', r'<span class="przypis">\1</a></span>'),
    (r'<font color="#FF0000"><b>(.*?)</a></b></font>', r'<span class="przypis">\1</a></span>'),
    (r'<center><font size="\+1"><font color="#008080">', '<span class="duzy_tytul">'),
    ('</font></font></center>', '</span>'),
    ('</font>', ''),
    ('<p align="JUSTIFY"><font color="#0000FF"><b>', '<span class="tytul">'),
    ('</b></font></p>', '</span>'),
    ('</b>', '</span>'),
    ('<font size="3"><p align="JUSTIFY">', '<p>'),
    ('<p align="JUSTIFY">', ''),
    (r'(</p>)+<span', '<span'),
    (r'</span></p>', '</span>'),
    ('<br></p></font>', '</p>'),
    (r'<a name="0*', '<a id="w'),
    (r'<img src="../NrRozdz/Roz0*([1-9]+\d*)\.gif" align="LEFT">', r'<span class="wielki_numer">\1</span>'),
    ('<br>', '<br/>'),
    (' target="Dolna"', '')
)

def bookContent(booknumber):
    url = masterURL + 'ksiega.php?id=' + booknumber
    doc = getPage(url)
    chapters =[]
    for data in doc.xpath('//select[@name="rozdzial"]/option'):
        bookNumber=''.join(data.xpath('./@value'))
        chapters.append(bookNumber)
    return chapters

def saveChapter(booknumber):
    url = 'http://biblia.deon.pl/ksiega.php?id=' + booknumber
    doc = getPage(url)
    start = 77 if 'T' in chapterLink.split('.')[0] else 114
    content = html.tostring(clean_html(doc))[start:-6]
    for fromPattern, toPattern in replaceStrings:
        content = re.sub(fromPattern, toPattern, content)
    if chapterLink == '001T.HTM':
        content = re.sub(r'<center><img src="Nazwa.gif"></center>', '<span class="tytul_ksiegi">' + bn.encode('utf-8') + '</span>', content)
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
        print chapterName, chapterLink
        saveChapter(bl,chapterLink,bn)
        index.append((bl,chapterName,chapterLink))

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

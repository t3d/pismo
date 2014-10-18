#!/usr/bin/python
# coding=utf-8

__license__ = 'GPL 3'
__copyright__ = '2012-2014, Tomasz Długosz <tomek3d@gmail.com>'

import urllib2
from lxml import html
import re

masterURL='http://biblia.deon.pl/'

def getPage(url):
    fetcher = urllib2.build_opener()
    fetcher.addheaders = [('User-agent', 'Mozilla/5.0')]
    response = fetcher.open(url)
    return html.fromstring(response.read())

def ToC():
    doc = getPage(masterURL)
    newTes = []
    oldTes = []
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
<link rel="stylesheet" type="text/css" href="style.css" />
<title>'''

css = '''
sup {font-size: 0.83em; vertical-align: super; line-height: 0; }
.tytul1 {font-weight:bold; text-align:center; }
.tytul2 {font-size:1.2em; text-align:center; }
.miedzytytul1 {font-weight:bold; text-align:center;}
.miedzytytul2 {font-style:italic; text-align:center;}
.miedzytytul3 {font-style:italic; font-size:0.8em; margin-left:-10px}
.werset {font-weight:bold; font-size: 0.6em; }
div.initial-letter { font-size:4.5em; line-height:0.9em; padding: 0 10px 0 0; float:left; }
'''

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
    ('<br>', '<br/>')
)


replaceStringsFootnotes = (
    ('a name=', 'a href='),
    (r'otworz\.php\?skrot=(.*?)%20(.*?),', r'\1\2.xhtml#WW'),
    (r'/rozdzial\.php\?id=(.*?)#', r'#W')
)

def bookContent(booknumber):
    url = masterURL + 'ksiega.php?id=' + booknumber
    doc = getPage(url)
    chapters =[]
    bookName = doc.xpath('//div[@class="book-label"]/text()')[0]
    for data in doc.xpath('//select[@name="rozdzial"]/option'):
        bookNumber=''.join(data.xpath('./@value'))
        chapters.append(bookNumber)
    return (chapters,bookName)

def saveChapter(chapterNumber,chapterFile,footnoteSeq):
    replaceStringsContent = (
        ('</font></font></center>', '</span>'),
        ('</font>', ''),
        ('</b></font></p>', '</span>'),
        ('</b>', '</span>'),
        (r'(</p>)+<span', '<span'),
        (r'</span></p>', '</span>'),
        ('<br></p></font>', '</p>'),
        (r'<a name="0*', '<a id="w'),
        (r'/rozdzial\.php\?id=(.*?)#', r'footnotes.xhtml#'+ chapterNumber )
    )
    url = masterURL + 'rozdzial.php?id=' + chapterNumber
    doc = getPage(url)
    content=html.tostring(doc.xpath('.//div[@class="tresc"]')[0])
    footnotes=(doc.xpath('.//div[@class="footnotes-content"]/p'))
    for fromPattern, toPattern in replaceStrings + replaceStringsContent:
        content = re.sub(fromPattern, toPattern, content)
    file = open(chapterFile, 'w')
    for footnote in footnotes:
        footnote = re.sub(r'#WW', chapterNumber + r'.xtml#WW',html.tostring(footnote))
        footnoteSeq.append(footnote)
    file.write(xhtmlHeader + str(chapterNumber) + '</title></head><body>' + content + '</body></html>')
    file.close()

def saveIndex(index):
    print 'generating INDEX...'
    indexfile = open('index.xhtml', 'w')
    indexfile.write(xhtmlHeader + 'index</title></head><body>')
    for chapterFile,chapterCounter,bookTitle in index:
        if chapterCounter == 1 :
            indexfile.write(bookTitle.encode('utf-8')  + '<br/>')
        indexfile.write('<a href=\"' + chapterFile + '">' + str(chapterCounter) + '</a> ')
    indexfile.write('</body></html>')
    indexfile.close()

def saveFootnotes(footnoteSeq):
    print 'saving footnotes...'
    footnotefile = open('footnotes.xhtml', 'w')
    footnotefile.write(xhtmlHeader + 'index</title></head><body>')
    for footnote in footnoteSeq:
        for fromPattern, toPattern in replaceStrings + replaceStringsFootnotes:
            footnote = re.sub(fromPattern, toPattern, footnote)
        footnotefile.write(footnote)
    footnotefile.write('</body></html>')
    footnotefile.close()

def saveCss():
    cssfile = open('style.css', 'w')
    cssfile.write(css)
    cssfile.close()

def getBook(index,footnoteSeq,bookNumber,bookShort):
    chapterNumbers,bookTitle= bookContent(bookNumber)
    print 'Working on book ' + bookTitle + '...'
    chapterCounter = 1
    for chapterNumber in chapterNumbers:
        chapterFile = bookShort + str(chapterCounter) + '.xhtml'
        saveChapter(chapterNumber,chapterFile,footnoteSeq)
        index.append((chapterFile,chapterCounter,bookTitle))
        '''
        if chapterCounter == 5:
            break
        '''
        chapterCounter+=1

stary,nowy = ToC()
index = []
footnoteSeq = []
for bookNumber, bookShort in stary:
    #print bookNumber, bookShort
    getBook(index,footnoteSeq,bookNumber,bookShort)
for bookNumber, bookShort in nowy:
    #print bookNumber, bookShort
    getBook(index,footnoteSeq,bookNumber,bookShort)
#getBook(index,footnoteSeq,'3','Kpł')
saveIndex(index)
if footnoteSeq :
    saveFootnotes(footnoteSeq)
saveCss()

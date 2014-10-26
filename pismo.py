#!/usr/bin/python
# coding=utf-8

__license__ = 'GPL 3'
__copyright__ = '2012-2014, Tomasz Długosz <tomek3d@gmail.com>'

import urllib2
from lxml import html
import unicodedata
import re

masterURL='http://biblia.deon.pl/'

def getPage(url):
    fetcher = urllib2.build_opener()
    fetcher.addheaders = [('User-agent', 'Mozilla/5.0')]
    response = fetcher.open(url)
    return html.fromstring(response.read())

def normalizeUnicode(name):
    return unicodedata.normalize('NFKD', name).encode('ascii','ignore')

def ToC():
    doc = getPage(masterURL)
    newTes = []
    oldTes = []
    bookNumber = 0
    bookShort = u''
    for data in doc.xpath('//select[@id="ksiega"]/option'):
        bookNumber=''.join(data.xpath('./@value'))
        bookShort=u''.join(data.xpath('./text()')).replace(' ','')
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
div.book-label{font-size:1.4em;text-align:center;}
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
    (r'otworz\.php\?skrot=(.*?)%20(.*?),', r'\1.xhtml#N\2W'),
    (r'Kp%C5%82(.xhtml)', r'Kp\1'),
    (r'%C5%81(k.xhtml)', r'\1'),
    (r'%20([0-9]{1,2}\.xhtml)', r'\1')
)

def bookContent(booknumber):
    url = masterURL + 'ksiega.php?id=' + booknumber
    doc = getPage(url)
    chapters =[]
    content=html.tostring(doc.xpath('.//div[@class="tresc"]')[0])
    footnotes=(doc.xpath('.//div[@class="footnotes-content"]/p'))
    bookName = doc.xpath('//div[@class="book-label"]/text()')[0]
    for data in doc.xpath('//select[@name="rozdzial"]/option'):
        bookNumber=''.join(data.xpath('./@value'))
        chapters.append(bookNumber)
    return (chapters[1:],bookName,content,footnotes)

def addChapter(bookFile,footnoteSeq,chapterCounter,chapterNumber=0,content='',footnotes=''):
    replaceStringsContent = (
        ('</font></font></center>', '</span>'),
        ('</font>', ''),
        ('</b></font></p>', '</span>'),
        ('</b>', '</span>'),
        (r'(</p>)+<span', '<span'),
        (r'</span></p>', '</span>'),
        ('<br></p></font>', '</p>'),
        (r'<a name="0*', '<a id="N'+ str(chapterCounter)),
        (r'/rozdzial\.php\?id=(.*?)#', r'footnotes.xhtml#'+ bookFile.split('.')[0] +'N' + str(chapterCounter))
    )
    if not content:
        url = masterURL + 'rozdzial.php?id=' + chapterNumber
        doc = getPage(url)
        content=html.tostring(doc.xpath('.//div[@class="tresc"]')[0])
        footnotes=(doc.xpath('.//div[@class="footnotes-content"]/p'))
    for fromPattern, toPattern in replaceStrings + replaceStringsContent:
        content = re.sub(fromPattern, toPattern, content)
    for footnote in footnotes:
        footnote = re.sub(r'/rozdzial\.php\?id=(.*?)#WW?', bookFile +'#N' + str(chapterCounter) + 'W',html.tostring(footnote))
        footnote = re.sub('<p><a name="P([0-9]+)"></a>', '<p id="' + bookFile.split('.')[0] +'N' + str(chapterCounter) + r'P\1">' ,footnote)
        footnoteSeq.append(footnote)
    return(content)

def saveIndex(index):
    print 'generating INDEX...'
    indexfile = open('index.xhtml', 'w')
    indexfile.write(xhtmlHeader + 'index</title></head><body>')
    for bookFile,bookNumber,bookTitle in index:
        indexfile.write('<a href=\"' + bookFile + '">' + bookTitle.encode('utf-8') + '</a>')
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
    chapterNumbers,bookTitle,content,footnotes = bookContent(bookNumber)
    print 'Working on book ' + bookTitle + '...'
    bookFile = normalizeUnicode(bookShort) + '.xhtml'
    file = open(bookFile, 'w')
    file.write(xhtmlHeader + bookTitle.encode('utf-8') + '</title></head><body><div class="book-label">'+ bookTitle.encode('utf-8')  + '</div>')
    file.write(addChapter(bookFile,footnoteSeq,1,content=content,footnotes=footnotes))
    chapterCounter = 2
    for chapterNumber in chapterNumbers:
        file.write(addChapter(bookFile,footnoteSeq,chapterCounter,chapterNumber=chapterNumber))
        '''
        if chapterCounter == 5:
            break
        '''
        chapterCounter+=1
    index.append((bookFile,bookNumber,bookTitle))
    file.write('</body></html>')
    file.close()

stary,nowy = ToC()
index = []
footnoteSeq = []
for bookNumber, bookShort in stary:
    #print bookNumber, bookShort
    getBook(index,footnoteSeq,bookNumber,bookShort)
for bookNumber, bookShort in nowy:
    #print bookNumber, bookShort
    getBook(index,footnoteSeq,bookNumber,bookShort)
#getBook(index,footnoteSeq,'3',u'Kpł')
saveIndex(index)
if footnoteSeq :
    saveFootnotes(footnoteSeq)
saveCss()

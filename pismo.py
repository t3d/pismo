#!/usr/bin/python
# coding=utf-8

__license__ = 'GPL 3'
__copyright__ = '2012-2014, Tomasz Długosz <tomek3d@gmail.com>'

import urllib2
from lxml import html
import unicodedata
import re
import tempfile
import shutil
import os
import zipfile
try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

masterURL='http://biblia.deon.pl/'
tmpdir = tempfile.mkdtemp()

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
    bookName = doc.xpath('//div[@class="book-label"]/text()')[0]
    for data in doc.xpath('//select[@name="rozdzial"]/option'):
        bookNumber=''.join(data.xpath('./@value'))
        chapters.append(bookNumber)
    return (chapters,bookName)

def addChapter(chapterNumber,bookFile,footnoteSeq,chapterCounter):
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
    url = masterURL + 'rozdzial.php?id=' + chapterNumber
    doc = getPage(url)
    content=html.tostring(doc.xpath('.//div[@class="tresc"]')[0])
    footnotes=(doc.xpath('.//div[@class="footnotes-content"]/p'))
    for fromPattern, toPattern in replaceStrings + replaceStringsContent:
        content = re.sub(fromPattern, toPattern, content)
    for footnote in footnotes:
        footnote = re.sub(r'/rozdzial\.php\?id=(.*?)#WW?', bookFile +'#N' + str(chapterCounter) + 'W',html.tostring(footnote))
        footnote = re.sub('a name="', 'a id="' + bookFile.split('.')[0] +'N' + str(chapterCounter) ,footnote)
        footnoteSeq.append(footnote)
    return(content)

def saveIndex(index):
    print 'generating INDEX...'
    indexfile = open(os.path.join(tmpdir, 'OEBPS', 'index.xhtml'), 'w')
    indexfile.write(xhtmlHeader + 'index</title></head><body>')
    for bookFile,bookNumber,bookTitle in index:
        indexfile.write('<a href=\"' + bookFile + '">' + bookTitle.encode('utf-8') + '</a>')
    indexfile.write('</body></html>')
    indexfile.close()

def saveFootnotes(footnoteSeq):
    print 'saving footnotes...'
    footnotefile = open(os.path.join(tmpdir, 'OEBPS', 'footnotes.xhtml'), 'w')
    footnotefile.write(xhtmlHeader + 'index</title></head><body>')
    for footnote in footnoteSeq:
        for fromPattern, toPattern in replaceStrings + replaceStringsFootnotes:
            footnote = re.sub(fromPattern, toPattern, footnote)
        footnotefile.write(footnote)
    footnotefile.write('</body></html>')
    footnotefile.close()

def saveCss():
    cssfile = open(os.path.join(tmpdir, 'OEBPS', 'style.css'), 'w')
    cssfile.write(css)
    cssfile.close()

def getBook(index,footnoteSeq,bookNumber,bookShort):
    chapterNumbers,bookTitle= bookContent(bookNumber)
    print 'Working on book ' + bookTitle + '...'
    chapterCounter = 1
    bookFile = normalizeUnicode(bookShort) + '.xhtml'
    file = open(os.path.join(tmpdir, 'OEBPS', bookFile), 'w')
    file.write(xhtmlHeader + bookTitle.encode('utf-8') + '</title></head><body><div class="book-label">'+ bookTitle.encode('utf-8')  + '</div>')
    for chapterNumber in chapterNumbers:
        content = addChapter(chapterNumber,bookFile,footnoteSeq,chapterCounter)
        file.write(content)
        '''
        if chapterCounter == 5:
            break
        '''
        chapterCounter+=1
    index.append((bookFile,bookNumber,bookTitle))
    file.write('</body></html>')
    file.close()

def epubBuild():
    os.mkdir(os.path.join(tmpdir,'META-INF'))
    os.mkdir(os.path.join(tmpdir,'OEBPS'))
    file = open(os.path.join(tmpdir,'mimetype'), 'w')
    print>>file, 'application/epub+zip'
    file.close()
    file = open(os.path.join(tmpdir,'META-INF','container.xml'), 'w')
    print>>file, '''<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
    <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
    </container>'''
    file.close()

def craftOpf():
    file = open(os.path.join(tmpdir, 'OEBPS', 'content.opf'), 'w')
    print>>file, '''<?xml version="1.0" encoding="UTF-8"?>
    <package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookID" version="2.0" >
        <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
            <dc:title>Biblia Tysiąclecia - Pismo Święte Starego i Nowego Testamentu</dc:title>
            <dc:language>pl-PL</dc:language>
            <dc:publisher>Wydawnictwo Pallottinum w Poznaniu</dc:publisher>
            <dc:identifier id="BookID" opf:scheme="UUID">ISBN 83-7014-218-4</dc:identifier>
        </metadata>
        <manifest>
            <item id="style" href="style.css" media-type="text/css" />
            <item id="footnotes" href="footnotes.xhtml" media-type="application/xhtml+xml" />'''
    spine=[]
    for bookFile,bookNumber,bookTitle in index:
        chapterId=bookFile.split('.')[0]
        file.write('            <item id="' + bookNumber + '" href="' + bookFile + '" media-type="application/xhtml+xml" />\n')
        spine.append(bookNumber)
    print>>file, '''    </manifest>
    <spine toc="ncx">'''
    for line in spine:
        file.write('            <itemref idref="' + line + '" />\n')
    print>>file, '''            <itemref idref="footnotes" />
    </spine></package>'''
    file.close()

def epubZip():
    print "zipping..."
    zf = zipfile.ZipFile('pismo.epub', mode='w')
    try:
        for root, dirs, files in os.walk(tmpdir):
            for name in files:
                zf.write(os.path.join(root,name),os.path.join(root.replace(tmpdir,'',1)[1:],name))
    finally:
        zf.close()

epubBuild()
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
craftOpf()
epubZip()
shutil.rmtree(tmpdir)

# -*- coding:utf-8 -*-
import requests
import re
from bs4 import BeautifulSoup
from collections import deque
import time
import random
import sys


file_network = open('edges.txt','wb') # fromNum'\t'toNum
file_rating = open('ratings.txt','wb') # userNum' 'itemNum' 'rating' 'category

userList = deque([])
userJudge = []
global recordCounter
global header
global proxy
global proxyList
recordCounter = 0
proxyList = []

def loadUserAgentFile():
    file_user_agent = open('user_agents.txt', 'r')
    agentList=[]
    for line in file_user_agent.readlines():
        agentList.append(line.strip())
    return agentList
userAgentList = loadUserAgentFile()

def getCookie():
    cookies = {}
    file_cookie = open('cookie.txt', 'r')  # loading cookie
    for line in file_cookie.read().split(';'):
        name, value = line.strip().split('=',1)
        cookies[name] = value
    return cookies

def getHeaders():
    global header
    index = random.randint(0, 899)
    header = {'User-Agent': userAgentList[index],
            'Connection':'closed'
            }
    return header

testUrl = 'https://www.douban.com/'
xiciUrl = 'http://www.xicidaili.com/nn'
def getWorkIp(url,testUrl):
    global header
    global proxy
    global proxyList
    header = getHeaders()
    req = requests.get(url,headers=header)
    html = req.content
    soup = BeautifulSoup(html,'html.parser')
    table = soup.find('table',attrs={'id':'ip_list'})
    trList = table.find_all('tr')
    trList.pop(0)
    for tr in trList:
        proxy = {}
        tdList = tr.find_all('td')
        ip = tdList[1].text.strip()
        port = tdList[2].text.strip()
        protocol = tdList[5].text.strip()
        ipAddress = ip+':'+port
        if protocol == 'HTTP' or protocol == 'HTTPS':
            ipAddress = protocol.lower()+'://'+ipAddress
            try:
                req = requests.get(testUrl,headers=header,proxies=proxy)
                if req.status_code == 200 :
                    proxy[protocol.lower()] = ipAddress
                    proxyList.append(proxy)
            except:
                continue

def getFriend(preUser,cookies,soup1):
    global header
    global proxy
    userJudge.append(preUser)
    div_friend = soup1.find('div',attrs={'id':'friend'})
    if div_friend != None:
        span_friend = div_friend.span
        friendListUrl = span_friend.a.attrs['href']
        # header = getHeaders()
        # proxy = getWorkIp(xiciUrl)
        req2 = requests.get(friendListUrl,headers=header,cookies=cookies,proxies=proxy)
        html2 = req2.content
        #file.write(html2)
        soup2 = BeautifulSoup(html2,'html.parser')
        div_List = soup2.find('div',attrs={'class':'article'})
        a_List = div_List.find_all('a',attrs={'class':'nbg'})
        for element in a_List:
            URL = str(element['href'])
            userListLine = URL.strip().split('/')
            networkLine = preUser + '\t' + userListLine[4]+'\n'
            file_network.write(networkLine)
            if userJudge.count(userListLine[4])==0:
                userList.append(userListLine[4])

def getMovieRating(preUser,soup):
    global recordCounter
    div_review = soup.find('div', attrs={'class': 'grid-view'})
    infoList = div_review.find_all('div', attrs={'class': 'info'})
    for infoLine in infoList:
        movieUrl = infoLine.a['href']
        ratingSection = infoLine.find_all('li')[2]
        ratingSubSection = ratingSection.find_all('span')
        for ratingLine in ratingSubSection:
            #print ratingLine['class']
            if ratingLine['class'][0] in ['date','comment','tags']:
                continue
            else :
                ratingValue = re.findall(r'\d+',str(ratingLine['class'][0]))
                if len(ratingValue) != 0 and ratingValue[0] <= '5' and ratingValue[0] >= '1':
                    movieNum = movieUrl.split('/')[4]
                    line = preUser+' '+ movieNum+' ' + ratingValue[0] + ' ' + '1' + '\n'

                    file_rating.write(line)
                    recordCounter +=1

def getMovie(preUser,soup,cookies):
    global header
    global proxy
    div_movie = soup.find('div',attrs={'id':'movie'})
    if div_movie != None:
        span_movie = div_movie.span
        movieList = span_movie.find_all('a')[-1]['href']
        # header = getHeaders()
        # proxy = getWorkIp(xiciUrl)
        req2 = requests.get(movieList,headers=header,cookies=cookies,proxies=proxy)
        html2 = req2.content
        #file1.write(html2)
        soup2 = BeautifulSoup(html2,'html.parser')
        div_paginator = soup2.find('div',attrs={'class':'paginator'})
        if div_paginator == None:
            getMovieRating(preUser,soup2)
        else:
            span_next = div_paginator.find('span',attrs={'class':'next'})
            a_next = span_next.a
            getMovieRating(preUser,soup2)
            while a_next != None:
                nextpageUrl = a_next['href']
                # header = getHeaders()
                # proxy = getWorkIp(xiciUrl)
                req3 = requests.get(nextpageUrl,headers=header,proxies=proxy)
                html3 = req3.content
                #file1.write(html2)
                soup3 = BeautifulSoup(html3,'html.parser')
                getMovieRating(preUser,soup3)
                div_paginator = soup3.find('div', attrs={'class': 'paginator'})
                span_next = div_paginator.find('span', attrs={'class': 'next'})
                a_next = span_next.a
                time.sleep(3)

def getBookRating(preUser,soup):
    global recordCounter
    div_article = soup.find('div', attrs={'class': 'article'})
    liList = div_article.find_all('li', attrs={'class': 'subject-item'})
    for li in liList:
        info = li.find('div', attrs={'class': 'info'})
        bookUrl = info.h2.a['href']
        bookNum = bookUrl.split('/')[4]
        div_short_note = info.find('div', attrs={'class': 'short-note'})
        spanList = div_short_note.div.find_all('span')
        for span in spanList:
            if span['class'][0] in ['date', 'comment', 'tags']:
                continue
            else:
                ratingLine = span['class']
                ratingValue = re.findall(r'\d+', str(ratingLine[0]))
                line = preUser + ' ' + bookNum + ' ' + ratingValue[0] + ' ' + '2' + '\n'
                file_rating.write(line)
                recordCounter += 1
        #time.sleep(2)

def getBook(preUser,soup,cookies):
    global header
    global proxy
    div_book = soup.find('div',attrs={'id':'book'})
    if div_book != None:
        span_book = div_book.span
        bookListUrl = span_book.find_all('a')[-1]['href']
        #print bookListUrl
        # header = getHeaders()
        # proxy = getWorkIp(xiciUrl)
        req2 = requests.get(bookListUrl,headers=header,cookies=cookies,proxies=proxy)
        html2 = req2.content
        #file2.write(html2)
        soup2 = BeautifulSoup(html2,'html.parser')
        div_paginator = soup2.find('div', attrs={'class': 'paginator'})
        if div_paginator == None:
            getBookRating(preUser, soup2)
        else:
            getBookRating(preUser, soup2)
            span_next = div_paginator.find('span',attrs={'class':'next'})
            a_next = span_next.a
            while a_next != None:
                nextpageUrl = a_next['href']
                # header = getHeaders()
                # proxy = getWorkIp(xiciUrl)
                req3 = requests.get(nextpageUrl, headers=header,proxies=proxy)
                html3 = req3.content
                soup3 = BeautifulSoup(html3, 'html.parser')
                getBookRating(preUser, soup3)
                div_paginator = soup3.find('div', attrs={'class': 'paginator'})
                span_next = div_paginator.find('span', attrs={'class': 'next'})
                a_next = span_next.a
                time.sleep(3)

def getMusicRating(preUser,soup):
    global recordCounter
    div_review = soup.find('div',attrs={'class':'grid-view'})
    ulList = div_review.find_all('ul')
    for ul in ulList:
        li = ul.find('li', attrs={'class': 'title'})
        musicUrl = li.a['href']
        #print musicUrl
        musicNum = musicUrl.split('/')[4]
        spanList = ul.find_all('span')
        for span in spanList:
            ratingLine = span['class']
            ratingValue = re.findall(r'\d+', str(ratingLine[0]))
            if len(ratingValue) != 0 and ratingValue[0] >= '1' and ratingValue[0] <= '5':
                line = preUser + ' ' + musicNum + ' ' + ratingValue[0] + ' ' + '3' + '\n'
                file_rating.write(line)
                recordCounter += 1
    #time.sleep(2)

def getMusic(preUser,soup,cookies):
    global header
    global proxy
    div_music = soup.find('div',attrs={'id':'music'})
    #print div_music
    if div_music != None:
        span_music = div_music.h2.span
        musicListUrl = span_music.find_all('a')[-1]['href']
        # header = getHeaders()
        # proxy = getWorkIp(xiciUrl)
        req2 = requests.get(musicListUrl,headers=header,cookies=cookies,proxies=proxy)
        html2 = req2.content
        #file3.write(html2)
        soup2 = BeautifulSoup(html2,'html.parser')
        div_paginator = soup2.find('div',attrs={'class':'paginator'})
        if div_paginator == None:
            getMusicRating(preUser,soup2)
        else :
            getMusicRating(preUser,soup2)
            span_next = div_paginator.find('span', attrs={'class': 'next'})
            a_next = span_next.a
            while a_next != None:
                nextpageUrl = a_next['href']
                # header = getHeaders()
                # proxy = getWorkIp(xiciUrl)
                req3 = requests.get(nextpageUrl,headers=header,proxies=proxy)
                html3 = req3.content
                soup3 = BeautifulSoup(html3,'html.parser')
                getMusicRating(preUser, soup3)
                div_paginator = soup3.find('div', attrs={'class': 'paginator'})
                span_next = div_paginator.find('span', attrs={'class': 'next'})
                a_next = span_next.a
                time.sleep(3)

def main():
    global recordCounter
    global header
    global proxy
    startUrl = 'https://www.douban.com/people/150269341/'
    preLine = startUrl.split('/')
    userList.append(preLine[4])
    #['https:', '', 'www.douban.com', 'people', 'Hazel.eyes', '']
    cookie = getCookie()
    userCounter = 1
    start = time.clock()
    #getWorkIp(xiciUrl)

    while len(userList)!=0 and userCounter <=5:
        getWorkIp(xiciUrl,testUrl)
        preUser = userList.popleft()
        userUrl = preLine[0]+'//'+preLine[2]+'/'+preLine[3]+'/'+preUser+'/'
        header = getHeaders()
        proxy = proxyList[0]
        req1 = requests.get(userUrl,headers=header,proxies=proxy)
        html1 = req1.content
        soup1 = BeautifulSoup(html1, 'html.parser')
        try:
            getFriend(preUser, cookie, soup1)
        except:
            header = getHeaders()
            Url = 'https://www.douban.com/people/' + preUser + '/contacts'
            for proxy in proxyList:
                req = requests.get(Url,headers=header,cookies=cookie,proxice=proxy)
                if req.status_code == 200:
                    break
            getFriend(preUser, cookie, soup1)
        print 'OK0'
        #print proxy
        try:
            getMovie(preUser, soup1,cookie)
        except:
            header = getHeaders()
            Url = 'https://movie.douban.com/people/'+preUser+'/collect'
            for proxy in proxyList:
                req = requests.get(Url,headers=header,cookies=cookie,proxice=proxy)
                if req.status_code == 200:
                    break
            getMovie(preUser, soup1,cookie)
        print 'OK1'
        #print proxy
        try:
            getMusic(preUser, soup1,cookie)
        except:
            header = getHeaders()
            Url = 'https://music.douban.com/people/'+preUser+'/collect'
            for proxy in proxyList:
                req = requests.get(Url,headers=header,cookies=cookie,proxice=proxy)
                if req.status_code == 200:
                    break
            getMusic(preUser, soup1,cookie)
        print 'OK2'
        print proxy
        try:
            getBook(preUser, soup1)
        except:
            header = getHeaders()
            Url = 'https://book.douban.com/people/' + preUser + '/collect'
            for proxy in proxyList:
                req = requests.get(Url, headers=header,cookies=cookie, proxice=proxy)
                if req.status_code == 200:
                    break
            getBook(preUser, soup1,cookie)
        print 'OK3'
        if userCounter %5 ==0:
            end = time.clock()
            cost = end - start
            print "%d lines cost: %f s" %(recordCounter ,cost)
        userCounter += 1
        time.sleep(2)

main()
file_network.close()
file_rating.close()
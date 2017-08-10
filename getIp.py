# -*-coding:gbk-*-
import requests
from bs4 import BeautifulSoup
import re
import random
import time
import types

#file_ip = open('testIp.html','r')
def loadUserAgentFile():
    file_user_agent = open('user_agents.txt', 'r')
    agentList=[]
    for line in file_user_agent.readlines():
        agentList.append(line.strip())
    return agentList

userAgentList = loadUserAgentFile()
testUrl = 'https://book.douban.com/'
global formerIP
formerIP = '0'
def getWorkIp(url):
    global formerIP
    start = time.clock()
    index = random.randint(0, 899)
    header = {'User-Agent': userAgentList[index],
              'Connection': 'closed'
              }
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
            proxy[protocol.lower()] = ipAddress
            try:
                print 'trying'
                print formerIP
                req = requests.get(testUrl,headers=header,proxies=proxy)
                if req.status_code == 200 and formerIP != ipAddress:
                    formerIP = ipAddress
                    end = time.clock()
                    print (end-start)
                    return ipAddress
            except:
                continue

xiciUrl = 'http://www.xicidaili.com/nn'
newIp = getWorkIp(xiciUrl)
new = getWorkIp(xiciUrl)
print newIp
print new

# coding=utf-8
import requests
import json
import time
import datetime
import redis

#r = redis.Redis('localhost', 6379,db=2)
r = redis.Redis(host='redis', port=6379, db=2)


headers = {'Host': 'weixin.91160.com',
           'Connection': 'keep-alive',
           'Origin': 'https://weixin.91160.com',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat QBCore/3.43.691.400 QQBrowser/9.0.2524.400',
           'Accept-Encoding': 'gzip, deflate',
           'Accept-Language': 'zh-CN,zh;q=0.8,en-us;q=0.6,en;q=0.5;q=0.4'}

while 1:
    cookie = r.lpop('91160:91160_cookie')
    if cookie:
        headers['Cookie'] = 'SHADOWMAN=%s' % cookie
        logined = requests.get(url='https://weixin.91160.com/notice/index.html', headers=headers)  # ,proxies={'https':'https://localhost:8888'},verify=False)
        print logined.status_code, cookie, datetime.datetime.now()
        r.rpush('91160:91160_cookie', cookie)
        time.sleep(10)
    else:
        print 'No cookie', datetime.datetime.now()
        time.sleep(1)

# coding=UTF-8
import redis
from lxml import etree
import time
import requests
import datetime
import json
import os
from pymongo import MongoClient


class guahao(object):

    def __init__(self, user, passwd, _id):
        self.user = user
        self.passwd = passwd
        self.r = redis.Redis(host='redis', port=6379, db=2)
        self._id = _id
        self.s = requests.session()
        self.headers = {'Host': 'weixin.91160.com',
                        'Connection': 'keep-alive',
                        'Origin': 'https://weixin.91160.com',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat QBCore/3.43.691.400 QQBrowser/9.0.2524.400',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept-Language': 'zh-CN,zh;q=0.8,en-us;q=0.6,en;q=0.5;q=0.4'}
        uri = 'mongodb://root:hayabusa!#$)@redis:27017'
        mongo_client = MongoClient(uri,connect=False)
        self.db = mongo_client['henan']

    def login(self):
        ##################登录#############################
        login_url = 'https://weixin.91160.com/user/login.html'
        data = {'username': self.user,
                'password': self.passwd}
        html = self.s.post(url=login_url, headers=self.headers, data=data)#, verify=False, proxies={'https': 'https://localhost:8888'})
        print 'login {}'.format(self.user)
        #################获取家庭成员编号#################
        member_url = 'https://weixin.91160.com/account/memberlist.html'
        member_html = self.s.get(url=member_url, headers=self.headers)#, verify=False, proxies={'https': 'https://localhost:8888'})
        member_selector = etree.HTML(member_html.content)
        member_ids = member_selector.xpath('*//div[@class="fullwidth flex mt10 fs0"]/div/@data-mid')
        return member_ids

    def guahao(self, member_id):
        self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat QBCore/3.43.691.400 QQBrowser/9.0.2524.400'
        try:
            # print u'#################预约url处理######################'
            sch_url = 'https://weixin.91160.com/doctor/detlnew.html?unit_detl_map=[{"unit_id":%d,"doctor_id":"%s","dep_id":%s,"schedule_id":"%s"}]' % (self._id['unit_id'], str(self._id['doctor_id']), str(self._id['dep_id']), str(self._id['sch_id']))
            sch_html = self.s.get(url=sch_url, headers=self.headers)#, verify=False, proxies={'https': 'https://localhost:8888'})
            detl_id = sch_html.json()['data'][self._id['sch_id']][0]['detl_id']
            #################token_url处理#####################
            token_url = 'https://weixin.91160.com/order/confirm.html?unit_id={}&sch_id={}&dep_id={}&detl_id={}'.format(self._id['unit_id'], self._id['sch_id'], self._id['dep_id'], detl_id)
            html = self.s.get(url=token_url, headers=self.headers)#, verify=True, proxies={'https': 'https://localhost:8888'})
            selector = etree.HTML(html.content)
            token_key = selector.xpath('*//input[@name="token_key"]//@value')[0]
            submit_url = 'https://weixin.91160.com/order/submit.html'
            submit_data = {'mobile': self.user,
                           'mid': member_id,
                           'insurance': '0',
                           'insurance_ztb': '1',
                           'casualty_zm': '0',
                           'is_use_order_service': '0',
                           'token_key': token_key}
            submit_html = self.s.post(url=submit_url, data=submit_data, headers=self.headers)#, verify=True, proxies={'https': 'https://localhost:8888'})
            result = json.loads(submit_html.content)
            html = self.s.get(url=token_url, headers=self.headers)#, verify=True, proxies={'https': 'https://localhost:8888'})
            selector = etree.HTML(html.content)
            token_key = selector.xpath('*//input[@name="token_key"]//@value')[0]
            self.db.jiuyi160.insert({'state':result['state'],'msg':result['msg'],'Time':str(datetime.datetime.now()),'member_id':member_id,'user':self.user})
        except Exception as e:
            print 'Error:%s' % str(e)

    def start(self):
        while 1:
            doc_yuyue_date = self.r.lindex('91160:%s' % self._id['doctor_id'], 0)
            if doc_yuyue_date:
                cookie = self.r.lpop('91160:91160_cookie')
                self.headers['Cookie'] = 'SHADOWMAN=%s' % cookie
                member_ids = self.login()
                self._id['sch_id'] = doc_yuyue_date
                for member_id in member_ids:
                    self.guahao(member_id)
                self.r.lpush('91160:91160_cookie', cookie)
                print 'push cookie to cookie_pool'
                os._exit(3)
            else:
                print 'No sch',self.user
                time.sleep(1)

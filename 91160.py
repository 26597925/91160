# coding=utf-8
import multiprocessing
import signal
import logging
import os
import errno
import requests
import json
import time
import datetime
from login import guahao
import redis
from settings import DOCTORS

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)-15s - %(levelname)s - %(message)s'
)
r = redis.Redis(host='redis', port=6379, db=1, password='hayabusa13401300cc')


def wait_child(signum, frame):
    logging.info('receive SIGCHLD')
    try:
        while True:
            cpid, status = os.waitpid(-1, os.WNOHANG)
            if cpid == 0:
                break
            exitcode = status >> 8
    except OSError as e:
        if e.errno == errno.ECHILD:
            print 'exit'
            logging.error('current process has no existing unwaited-for child processes.')
        else:
            raise
    logging.info('handle SIGCHLD end')


signal.signal(signal.SIGCHLD, wait_child)


headers = {'Host': 'weixin.91160.com',
           'Connection': 'keep-alive',
           'Origin': 'https://weixin.91160.com',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat QBCore/3.43.691.400 QQBrowser/9.0.2524.400',
           'Accept-Encoding': 'gzip, deflate',
           'Accept-Language': 'zh-CN,zh;q=0.8,en-us;q=0.6,en;q=0.5;q=0.4'}
r = redis.Redis(host='redis', port=6379, db=2, password='hayabusa13401300cc')
if __name__ == '__main__':
    while 1:
        user_passwd_doctor = r.lpop('91160:user_passwd_doctor')
        if user_passwd_doctor:
            user_passwd_doctor = user_passwd_doctor.split(',')
            user = user_passwd_doctor[0]
            passwd = user_passwd_doctor[1]
            doctor_ids = DOCTORS[user_passwd_doctor[-1]]
            _id = {}
            _id['unit_id'] = int(doctor_ids['unit_id'])
            _id['doctor_id'] = doctor_ids['doctor_id']
            _id['dep_id'] = doctor_ids['dep_id']
            r.lpush('91160:unit_dep_doctor', '%s,%s,%s' % (_id['unit_id'], _id['dep_id'], _id['doctor_id']))
            yuyue = guahao(user, passwd, _id)
            p = multiprocessing.Process(target=yuyue.start)
            p.start()
        else:
            print 'No user_passwd_doctor'
            time.sleep(1)

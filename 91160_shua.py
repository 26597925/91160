# coding=utf-8
import requests
import json
import time
import signal
import errno
import logging
import datetime
import redis
import os
import multiprocessing


#r = redis.Redis('localhost', 6379, db=1)
r = redis.Redis(host='redis', port=6379, db=2, password='hayabusa13401300cc')


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)-15s - %(levelname)s - %(message)s'
)

def get_sch(unit_id, dep_id, doctor_id):
    sch_url = 'https://weixin.91160.com/doctor/schedule.html?unit_id=%s&doctor_ids=%s' % (unit_id, doctor_id)
    print sch_url
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/64.0.3282.119 Chrome/64.0.3282.119 Safari/537.36'}
    s = requests.session()
    while 1:
        try:
            html = s.get(sch_url, headers=headers).json()
            doc_key = '%s_%s' % (dep_id, doctor_id)
            html = html['sch'][unit_id][doc_key]
            _id = {}
            for value in html.values():
                for va in value.values():
                    for v in va['sch'].values():
                        if int(v['y_state']) != 0:
                            print 'get'
                            r.lpush('91160:%s' % doctor_id, v['schedule_id'])
                            os._exit(3)
                            break
                        else:
                            print 'No sch', v['to_date'], v['y_state_desc'], doctor_id, datetime.datetime.now()
        except Exception as e:
            print e
        time.sleep(1)

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

if __name__ == '__main__':
    while 1:
        unit_dep_doctor = r.lpop('91160:unit_dep_doctor')
        if unit_dep_doctor:
            unit_dep_doctor = unit_dep_doctor.split(',')
            unit_id = unit_dep_doctor[0]
            dep_id = unit_dep_doctor[1]
            doctor_id = unit_dep_doctor[-1]
            if unit_id and dep_id and doctor_id:
                p = multiprocessing.Process(target=get_sch,args=(unit_id, dep_id, doctor_id,))
                p.start()
        else:
            print 'No doctor_id'
            time.sleep(10)

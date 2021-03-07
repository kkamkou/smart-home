from threading import Thread, Semaphore
from time import sleep

import schedule

from instance import args, instance_config
from lib import RestApi
from sensors.dispatch import dispatch

args = args()
config = instance_config(getattr(args, 'config'), getattr(args, 'environment'))
lock = Semaphore(len(config['sensors']))
api = RestApi(config['api']['url'], config['api']['user'])


def job(timeout: int):
    instance = Thread(target=dispatch, args=(sensor, api, lock), daemon=True)
    instance.start()
    lock.acquire()
    instance.join(timeout=timeout)


for sensor in filter(lambda s: s.get("interval", None) > 0, config['sensors']):
    schedule.every(sensor['interval']).seconds.do(job, sensor.get('timeout', 1))

while True:
    schedule.run_pending()
    sleep(1)

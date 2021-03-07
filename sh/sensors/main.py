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


def job(sensor: dict):
    instance = Thread(target=dispatch, args=(sensor, api, lock), daemon=True)
    instance.start()
    lock.acquire()
    instance.join(timeout=sensor.get('timeout', 1))


for entry in filter(lambda s: s.get("interval", -1) > 0, config['sensors']):
    schedule.every(entry['interval']).seconds.do(job, entry)

while True:
    schedule.run_pending()
    sleep(1)

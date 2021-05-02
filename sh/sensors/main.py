from threading import Thread, Semaphore
from time import sleep

import schedule

from instance import args, instance_config, instance_db
from lib import RestApi
from sensors.dispatch import dispatch

args = args()
config = instance_config(getattr(args, 'config'), getattr(args, 'environment'))
lock = Semaphore(len(config['sensors']))
api = RestApi(config['api']['url'], config['api']['user'])
db = instance_db(config['influxdb'])


def job(sensor: dict):
    instance = Thread(target=dispatch, args=(sensor, api, db, lock), daemon=True)
    instance.start()

    if not lock.acquire(timeout=10):
        raise RuntimeError('Unable to acquire a new lock')


for entry in filter(lambda s: s.get('interval', -1) > 0, config['sensors']):
    schedule.every(entry['interval']).seconds.do(job, entry)

while True:
    schedule.run_pending()
    sleep(1)

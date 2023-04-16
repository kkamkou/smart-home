from threading import current_thread, Semaphore

from influxdb import InfluxDBClient

import sensors.mappings
from instance import instance_logging
from lib import RestApi


def dispatch(sensor, api: RestApi, db: InfluxDBClient, lock: Semaphore) -> None:
    log = instance_logging(__name__)
    log.info('Thread: %s, %s', current_thread().name, sensor)

    entries = filter(lambda e: e['name'] == sensor['name'], api.sensors().values())

    try:
        if not entries:
            raise RuntimeError(f"Unable to find [{sensor['name']}] sensor")

        for entry in entries:
            cls = str(entry['type']).replace('ZHA', 'Zha', 1)
            model = getattr(sensors.mappings, cls)(entry)
            db.write_points([{
                'measurement': model.type(),
                'tags': {'sensor': model.id(), 'name': sensor['name'], 'type': model.type()},
                'time': model.timestamp(),
                'fields': {'value': model.value()}
            }])
    finally:
        lock.release()

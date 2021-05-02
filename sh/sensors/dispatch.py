from threading import current_thread, Semaphore

from influxdb_client import Point, InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

import sensors.mappings
from instance import instance_logging
from lib import RestApi


def dispatch(sensor, api: RestApi, db: InfluxDBClient, lock: Semaphore) -> None:
    log = instance_logging(__name__)
    log.info('Thread: %s, %s', current_thread().getName(), sensor)

    entries = filter(lambda e: e['name'] == sensor['name'], api.sensors().values())
    if not entries:
        lock.release()
        raise RuntimeError('Unable to find "{}" sensor'.format(sensor['name']))

    try:
        write_api = db.write_api(write_options=SYNCHRONOUS)
        for entry in entries:
            cls = str(entry['type']).replace("ZHA", "Zha", 1)
            model = getattr(sensors.mappings, cls)(entry)
            write_api.write(
                bucket="sensors",
                record=Point(model.type())
                       .field("value", model.value())
                       .tag("sensor", model.id())
                       .tag("name", sensor['name'])
                       .tag("type", model.type())
                       .time(model.timestamp())
            )
    finally:
        lock.release()

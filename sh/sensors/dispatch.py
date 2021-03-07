from threading import current_thread, Semaphore

import sensors.mappings
from instance import instance_logging, instance_db_connection, instance_db_session
from lib import RestApi
from lib.models import SensorHistory, Base


def dispatch(sensor, api: RestApi, lock: Semaphore) -> None:
    db_connection = instance_db_connection(sensor['database']).connect()
    db_session = instance_db_session(db_connection)

    Base.metadata.create_all(db_connection)

    log = instance_logging(__name__)

    log.info('Thread: %s, %s', current_thread().getName(), sensor)
    entry = next(filter(lambda e: e['name'] == sensor['name'], api.sensors().values()), None)
    if not entry:
        raise RuntimeError('Unable to find "{}" sensor'.format(sensor['name']))

    cls = str(entry['type']).replace("ZHA", "Zha", 1)
    model = getattr(sensors.mappings, cls)(entry)

    record = SensorHistory(sensor=model.id(), value=model.value(), timestamp=model.timestamp(), type=model.type())
    if not db_session.query(SensorHistory).filter(SensorHistory.timestamp == record.timestamp).first():
        db_session.add(record)
        db_session.commit()

    db_connection.invalidate()
    lock.release()

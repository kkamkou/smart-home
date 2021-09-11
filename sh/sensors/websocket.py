import asyncio
import json
from asyncio import sleep, create_task
from datetime import datetime

import websockets

from instance import args, instance_config, instance_logging, instance_db

args = args()
config = instance_config(getattr(args, 'config'), getattr(args, 'environment'))
log = instance_logging(__name__, 10)
db = instance_db(config['influxdb'])


async def process(ws):
    payload = json.loads(await ws.recv())
    if payload['t'] != 'event':
        log.warning('Unable to interpret "%s" payload', payload)
        return

    log.debug(f"< {payload}")

    if 'state' not in payload or 'uniqueid' not in payload:
        log.debug(f'Unable to process the event: {payload!r}')
        return

    create_task(persist(payload))

    for listener in filter(
        lambda x: 'device' not in x or x['device'] == payload['uniqueid'],
        config['listeners']
    ):
        for trigger in filter(lambda x: x['state'].items() & payload['state'].items(), listener['triggers']):
            log.debug(f'Triggering "{trigger!r}"')
            if trigger['type'] == 'script':
                create_task(run(trigger['params']['path']))


async def persist(payload):
    last_updated = datetime.fromisoformat(payload['state']['lastupdated']) if 'lastupdated' in payload['state'] \
        else datetime.now()
    db.write_points([{
        'measurement': payload['r'],
        "tags": {'sensor': payload['uniqueid']},
        'time': last_updated,
        'fields': dict(filter(lambda v: not isinstance(v[1], list), payload['state'].items()))
    }])


async def run(cmd):
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    if proc.returncode:
        msg = f'{cmd!r} exited with {proc.returncode}'
        if stdout:
            msg += f'\n\t[stdout]: {stdout.decode()}'
        if stderr:
            msg += f'\n\t[stderr]: {stderr.decode()}'
        log.warning(msg)


async def connect():
    log.info(f"Connecting to {config['websockets']['uri']}...")
    async with websockets.connect(config['websockets']['uri']) as websocket:
        try:
            while True:
                await process(websocket)
                await sleep(0.1)
        except Exception as e:
            log.error(e)
            create_task(websocket.close())
            await sleep(5)
            await connect()


asyncio.get_event_loop().run_until_complete(connect())

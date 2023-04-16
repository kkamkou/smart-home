import asyncio
import json
from asyncio import sleep, create_task
from datetime import datetime
from importlib import import_module

import websockets

from instance import args, instance_config, instance_logging, instance_db
from lib import RestApi
from scene import AbstractScene

args = args()
config = instance_config(getattr(args, 'config'), getattr(args, 'environment'))
api = RestApi(config['api']['url'], config['api']['user'])
db = instance_db(config['influxdb'])
log = instance_logging(__name__, 10)


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
        config['websockets']['listeners']
    ):
        for trigger in filter(lambda x: x['state'].items() & payload['state'].items(), listener['triggers']):
            if 'disabled' in trigger and trigger['disabled']:
                continue

            log.debug(f'Triggering "{trigger!r}"')

            if trigger['type'] == 'script':
                create_task(run_shell(trigger['params']['path']))
            elif trigger['type'] == 'scene':
                create_task(run_scene(trigger['name'], trigger['params'], payload))


async def persist(payload):
    last_updated = datetime.fromisoformat(payload['state']['lastupdated']) if 'lastupdated' in payload['state'] \
        else datetime.now()
    db.write_points([{
        'measurement': payload['r'],
        'tags': {'sensor': payload['uniqueid']},
        'time': last_updated,
        'fields': dict(filter(lambda v: not isinstance(v[1], list), payload['state'].items()))
    }])


async def run_scene(name: str, params: dict, payload: dict) -> None:
    scene_name = f'{name.title()}Scene'

    log.debug(f'Running scene [{scene_name}]')

    try:
        instance: AbstractScene = getattr(import_module('scene'), scene_name)(api, params, payload)
        instance.run()
        log.debug(f'Scene {scene_name} complete')
    except Exception as e:
        log.error(f'Unable to run a scene [{scene_name}]: {e}')


async def run_shell(cmd):
    log.debug(f'Running shell [{cmd}]')

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
                await asyncio.gather(process(websocket), sleep(0.1))
        except Exception:
            log.exception('Exception during execution')
            await asyncio.gather(websocket.close(), sleep(5), connect())

asyncio.new_event_loop().run_until_complete(connect())

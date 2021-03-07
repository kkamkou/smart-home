from argparse import ArgumentParser

import requests

from ant.easy.channel import Channel
from ant.easy.node import Node
from instance import args
from sh.instance import instance_config, instance_logging

parser = ArgumentParser()
parser.add_argument('--environment', metavar='environment', type=str, choices=['development', 'production'])
parser.add_argument('--config', metavar='PATH', type=str)

args = args()
config = instance_config(getattr(args, 'config'), getattr(args, 'environment'))
log = instance_logging(__name__)

threads = []


def zz(data):
    d = requests.put("http://localhost/api/F22364914F/lights/7/state", json={"hue": 3000, "sat": 255, "bri": 255})
    print(d)


for device in config['devices']:
    node = Node()

    print(config["network"]["key"])

    node.set_network_key(0x00, [0xB9, 0xA5, 0x21, 0xFB, 0xBD, 0x72, 0xC3, 0x45])

    channel = node.new_channel(Channel.Type.BIDIRECTIONAL_RECEIVE)

    channel.on_broadcast_data = zz
    channel.on_burst_data = zz

    log.info(device["id"], device["type"])

    channel.set_period(8070)
    channel.set_search_timeout(12)
    channel.set_rf_freq(57)
    channel.set_id(device["id"], device["type"], 1)

    try:
        channel.open()
        node.start()
    finally:
        node.stop()

    # instance = Thread(target=dispatch, args=(device, config), daemon=True)
    # threads.append(instance)
    # instance.start()

"""
from queue import PriorityQueue
queue = PriorityQueue()
for item in topic.listen():
    try:
        data = item.get('data').decode('utf-8') if isinstance(item.get('data'), bytes)\
            else '{{"payload": {}}}'.format(item.get('data'))
    except Exception as e:
        log.error("Unable to interpret the payload (%s)", item.get('data'))
        continue

    message = RedisMessage(
        RedisMessageBody(data),
        item.get('type'),
        item.get('pattern').decode('utf-8') if item.get('pattern') is not None else None,
        item.get('channel').decode('utf-8')
    )

    if message.type() == 'subscribe':
        log.info(
            'Subscribed to: "%s". Channels currently subscribed to: %d',
            message.channel(), message.data().to_dict().get('payload')
        )
        continue

    if message.type() != 'message':
        log.warning('Unsupported message type "%s"', message.type())
        continue

    request = RedisRequest(message)

    # the current version check
    if request.version() is not 1:
        log.warning('Unsupported message version "%d"', request.version())
        continue

    log.debug("A new request\n%s", str(request))

    queue.put((request.priority(), request))

    qsize = queue.qsize()
    threads_size = len(threads)

    if threads_size < 1 or qsize >= int(config['load_per_thread']) * (threads_size or 1):
        threads = list(filter(lambda thread: thread.isAlive(), threads))

        instance = Thread(target=dispatch, args=(queue, config), daemon=True)
        threads.append(instance)
        instance.start()

        log.info('A new thread has been spawned. Threads: %d. Queue size: %d', threads_size, qsize)
"""

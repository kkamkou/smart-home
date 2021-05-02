"""
from threading import current_thread

from ant.easy.node import Node
from ant.easy.channel import Channel

from sh.instance import instance_logging


def dispatch1(device, config) -> None:
    log = instance_logging(__name__)

    log.info('Thread: %s, %s', current_thread().getName(), device)

    def on_data(data):
        print("Heartrate: " + str(data[7]) + " [BPM]")

    node = Node()

    node.set_network_key(0x00, config["network"]["key"])

    channel = node.new_channel(Channel.Type.BIDIRECTIONAL_RECEIVE)

    channel.on_broadcast_data = on_data
    channel.on_burst_data = on_data

    channel.set_period(8070)
    channel.set_search_timeout(12)
    channel.set_rf_freq(57)
    channel.set_id(0, 120, 0)

    try:
        log.info(0)
        channel.open()
        log.info(1)
        node.start()
        log.info(2)
    finally:
        node.stop()


"""

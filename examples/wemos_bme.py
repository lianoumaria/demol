#!/usr/bin/env python

import sys
import time
import random

from commlib.msg import MessageHeader, PubSubMessage
from commlib.node import Node, TransportType


class EnvMessage(PubSubMessage):
    # header: MessageHeader = MessageHeader()
    humidity: float = -1
    temperature: float = -1
    pressure: float = -1
    gas: float = -1


if __name__ == '__main__':
    from commlib.transports.mqtt import ConnectionParameters
    conn_params = ConnectionParameters(
        host="155.207.19.66",
        port=1883,
        username="r4a",
        password="r4a123$"
    )

    node = Node(node_name='wemos',
                connection_params=conn_params,
                debug=True)

    pub = node.create_publisher(msg_type=EnvMessage,
                                topic='pandora.wemos.env')

    node.run()

    while True:
        msg = EnvMessage(
            humidity=random.uniform(0.1, 1),
            temperature=random.uniform(20, 40),
            pressure=101.325,
            gas=random.uniform(0, 1)
        )
        pub.publish(msg)
        time.sleep(1)

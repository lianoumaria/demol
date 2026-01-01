from commlib.node import Node
from commlib.transports.mqtt import ConnectionParameters
from commlib.utils import Rate
from .msg import LedArrayMessage
from .ws2812 import WS2812


if __name__ == "__main__":
    rate = 30.0
    actuator = WS2812(attributes={'num_leds': 12, 'color_format': 'GRB', 'brightness': 0.5}, conn={'gpio': {'pins': {'DIN': {'name': 'GPIO10', 'id': 19}}}})
    actuator.initialize()
    conn_params = ConnectionParameters(host="localhost", port=1883, ssl=False)
    node = Node(
        node_name='actuators.LedArray',
        connection_params=conn_params,
        heartbeats=False)
    sub = node.subscriber(
        msg_type=LedArrayMessage,
        topic="my_raspi.actuators.ws2812.MyLedRing",
        on_message=actuator.write)
    node.run_forever(sleep_rate=rate)
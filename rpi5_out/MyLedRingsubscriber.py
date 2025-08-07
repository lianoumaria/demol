import time
from commlib.node import Node
from commlib.transports.mqtt import ConnectionParameters
from commlib.msg import MessageHeader, PubSubMessage

class SensorMessage(PubSubMessage):
    header: MessageHeader = MessageHeader()
    data : dict = {}

def on_message(msg):
    print(f'Received data: {msg}')

if __name__ == '__main__':
    conn_params = ConnectionParameters(host="localhost", port=1883)

    node = Node(node_name='node.WS2812', connection_params=conn_params)

    node.create_subscriber(msg_type=SensorMessage,
                           topic="my_raspi.actuators.ws2812.MyLedRing",
                           on_message=on_message)  # Define a callback function

    node.run_forever(sleep_rate=1)  # Define a process-level sleep rate in hz
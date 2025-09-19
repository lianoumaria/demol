import time
from commlib.node import Node
from commlib.transports.mqtt import ConnectionParameters
#from commlib.msg import MessageHeader, PubSubMessage
from MQTTMessages import DistanceMessage

def on_message(msg):
    print(f'Received data: {msg}')

if __name__ == '__main__':
    conn_params = ConnectionParameters(host="localhost", port=1883)

    node = Node(node_name='node.SRF05', connection_params=conn_params)

    node.create_subscriber(msg_type=DistanceMessage,
                           topic="my_raspi.sensor.distance.mysrf",
                           on_message=on_message)  # Define a callback function

    node.run_forever(sleep_rate=1)  # Define a process-level sleep rate in hz
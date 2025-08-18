import time

from MyLedRing import WS2812
from commlib.node import Node
from commlib.transports.mqtt import ConnectionParameters
from commlib.msg import MessageHeader, PubSubMessage

FREQUENCY = 1

class SensorMessage(PubSubMessage):
    header: MessageHeader = MessageHeader()
    data : dict = {}

def sample(msg):
    global FREQUENCY
    sensor = WS2812()
    if FREQUENCY == 0:
        raise ValueError("Frequency zero is not valid")
    elif FREQUENCY > sensor.get_max_frequency():
        FREQUENCY = sensor.get_max_frequency()
        print(f"Sampling at {FREQUENCY} Hz.")
    period = 1/FREQUENCY
    try:
        while True:
            pub.publish(msg)
            msg.data = sensor.read_data()
            time.sleep(period)
    except KeyboardInterrupt:
            sensor.disconnect()
    
if __name__ == "__main__":
    conn_params = ConnectionParameters(host="localhost", port=1883)
    node = Node(node_name='sensors.WS2812', connection_params=conn_params)
    pub = node.create_publisher(msg_type=SensorMessage, topic="rpicomplete.actuator.ledarray.myledring")
    node.run()
    msg = SensorMessage()
    sample(msg = msg)
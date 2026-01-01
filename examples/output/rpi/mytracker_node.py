from commlib.node import Node
from commlib.transports.mqtt import ConnectionParameters
from .msg import ProximityMessage
from .tcrt5000 import TCRT5000


if __name__ == "__main__":
    sensor = TCRT5000(attributes={'frequency': 100}, conn={'gpio': {'pins': {'D0': {'name': 'GPIO4', 'id': 7}}}})
    sensor.initialize()
    conn_params = ConnectionParameters(host="localhost", port=1883, ssl=False)
    node = Node(node_name='sensors.Proximity', connection_params=conn_params, heartbeats=False)
    pub = node.create_publisher(msg_type=ProximityMessage, topic="my_raspi.sensors.tracker.TCRT5000")
    try:
        node.run()
        while True:
            sensor.read()
            pub.send(self.msg)
            self._rate.sleep()
    except KeyboardInterrupt:
        sensor.disconnect()
    except Exception as e:
        print(e)
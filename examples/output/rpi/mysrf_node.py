from commlib.node import Node
from commlib.transports.mqtt import ConnectionParameters
from .msg import DistanceMessage
from .srf05 import SRF05


if __name__ == "__main__":
    sensor = SRF05(attributes={'frequency': 10.0}, conn={'gpio': {'pins': {'trigger': {'name': 'GPIO23', 'id': 16}, 'echo': {'name': 'GPIO24', 'id': 18}}}})
    sensor.initialize()
    conn_params = ConnectionParameters(host="localhost", port=1883, ssl=False)
    node = Node(node_name='sensors.Distance', connection_params=conn_params, heartbeats=False)
    pub = node.create_publisher(msg_type=DistanceMessage, topic="my_raspi.sensors.distance.srf05")
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
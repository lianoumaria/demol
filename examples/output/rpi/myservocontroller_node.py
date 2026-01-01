from commlib.node import Node
from commlib.transports.mqtt import ConnectionParameters
from commlib.utils import Rate
from .msg import ServoControllerMessage
from .pca9685 import PCA9685


if __name__ == "__main__":
    rate = 50
    actuator = PCA9685(attributes={'channels': 16, 'frequency': 50}, conn={'i2c': {'bus': 0, 'slave_address': '0x64', 'pins': {'sda': {'name': 'GPIO2', 'id': 3}, 'scl': {'name': 'GPIO3', 'id': 5}}}})
    actuator.initialize()
    conn_params = ConnectionParameters(host="localhost", port=1883, ssl=False)
    node = Node(
        node_name='actuators.ServoController',
        connection_params=conn_params,
        heartbeats=False)
    sub = node.subscriber(
        msg_type=ServoControllerMessage,
        topic="rpicomplete.actuator.servocontroller.myservocontroller",
        on_message=actuator.write)
    node.run_forever(sleep_rate=rate)
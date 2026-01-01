from commlib.node import Node
from commlib.transports.mqtt import ConnectionParameters
from .msg import EnvMessage
from .bme680 import BME680


if __name__ == "__main__":
    sensor = BME680(attributes={'poll_period': 10, 'humidity_oversample': 2, 'pressure_oversample': 4, 'temperature_oversample': 8, 'filter_size': 3, 'gas_status': 'ENABLE_GAS_MEAS', 'heater_temp': 320, 'heater_duration': 150, 'heater_profile': 0}, conn={'i2c': {'bus': 0, 'slave_address': '0x76', 'pins': {'sda': {'name': 'GPIO2', 'id': 3}, 'scl': {'name': 'GPIO3', 'id': 5}}}})
    sensor.initialize()
    conn_params = ConnectionParameters(host="localhost", port=1883, ssl=False)
    node = Node(node_name='sensors.Env', connection_params=conn_params, heartbeats=False)
    pub = node.create_publisher(msg_type=EnvMessage, topic="my_raspi.sensors.env.bme680")
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
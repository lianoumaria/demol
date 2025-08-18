from commlib.msg import MessageHeader, PubSubMessage

class DistanceMessage(PubSubMessage):
    header: MessageHeader = MessageHeader()
    distance: float = 0.0
    unit: str = "cm" #This won't change
    max_distance : float = 200.0
    min_distance : float = 0.0

class EnvMessage(PubSubMessage):
    header: MessageHeader = MessageHeader()
    temperature : float = 25.0
    pressure : float = 1013.25
    humidity : float = 45.00
    gas_resistance : float = 50000.0

class TrackerMessage(PubSubMessage):
    header: MessageHeader = MessageHeader()
    object_detection : bool = 0
    color : str = "Black"

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

class LedArrayMessage(PubSubMessage):
    header: MessageHeader = MessageHeader()
    colors : list = (  # defined in the device
        0xFF0000,  # Red
        0x00FF00,  # Green
        0x0000FF,  # Blue
        0xFFFF00,  # Yellow
        0xFF00FF,  # Magenta
        0x00FFFF,  # Cyan
        0xFFFFFF,  # White
        0x800000,  # Maroon
        0x008000,  # Dark Green
        0x000080,  # Navy
        0xFFA500,  # Orange
        0x800080,  # Purple
    )
    delay: float = 0.1 
    brightness: float = 0.5
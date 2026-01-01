from gpiozero import DistanceSensor as DS
from time import sleep

TRIGGER_PIN = "GPIO23"
TRIGGER_PIN_NUMBER = "16"
ECHO_PIN = "GPIO24"
ECHO_PIN_NUMBER = "18"


class SRF05(Sensor):
    #The class that sums up all distance sensors

    def __init__(self):
        self.max_distance = MAX_DISTANCE
        self.min_distance = MIN_DISTANCE
        self.max_frequency = MAX_FREQUENCY
        self.sensor = DS(
            trigger=TRIGGER_PIN,
            echo=ECHO_PIN,
            max_distance=self.max_distance,
            threshold_distance=0.3
        )
        self.msg = DistanceMessage()
    
    def read(self):
        data = {
            "distance": self.sensor.distance * 100,
            "max_distance": self.max_distance,
            "min_distance": self.min_distance
        }
        self.msg = DistanceMessage(**data)
        return msg
    
    def get_max_frequency(self):
        return self.max_frequency

    def disconnect(self):
        self.sensor.close()
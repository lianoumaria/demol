from gpiozero import DistanceSensor as DS
from time import sleep


MAX_FREQUENCY = 49  #(Hz) recommended 
MAX_DISTANCE = 400
MIN_DISTANCE = 2
TRIGGER_PIN = "GPIO23"
ECHO_PIN = "GPIO24"


class Distance_sensor:
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
    
    def read_data(self):
        #The distance is returned in centimeters
        data = {
            #"sensor_name": "SRF05",
            "distance": self.sensor.distance * 100,
            "max_distance": self.max_distance,
            "min_distance": self.min_distance
        }
        return data
    
    def get_max_frequency(self):
        return self.max_frequency


    def disconnect(self):
        #Release used resources
        self.sensor.close()

class SRF05(Distance_sensor):
    pass
    
class HCSR04(Distance_sensor):
    pass
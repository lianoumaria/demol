from gpiozero import DistanceSensor as DS
from time import sleep

MAX_SRF05_DISTANCE = 4.0
MAX_HC_SR04_DISTANCE = 4.0

class DistanceSensor:
    #The class that sums up all distance sensors

    def __init__(self, trigger, echo, max_distance=2.0, threshold_distance=0.3):
        self.sensor = DS(
            trigger=trigger,
            echo=echo,
            max_distance=max_distance,
            threshold_distance=threshold_distance
        )
    
    def read_sensor(self):
        #The distance is returned in centimeters
        return self.sensor.distance * 100  # Convert from meters to centimeters
    
    def disconnect(self):
        #Release used resources
        self.sensor.close()

class SRF05(DistanceSensor):
    pass

class HC_SR04(DistanceSensor):
    pass







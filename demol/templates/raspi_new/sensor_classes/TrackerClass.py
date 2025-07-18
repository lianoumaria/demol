from gpiozero import DigitalInputDevice as DInD
import time

class TrackerSensor:
    #The sensor recognizes whether it "sees" black or a white/reflective area
    def __init__(self, gpio_pin):
        self.sensor = DInD(gpio_pin)
    
    def read_sensor(self):
        return self.sensor.value

    def disconnect(self):
        #Release used resources
        self.sensor.close()

class HW006(TrackerSensor):
    # I can add restrictions here specific to the tracker sensor model
    pass

class TCRT5000(TrackerSensor):
    pass
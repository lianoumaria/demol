from gpiozero import DigitalInputDevice as DInD
import time

GPIO_PIN = "GPIO4"
MAX_FREQUENCY = 3000

class TrackerSensor:
    #The sensor recognizes whether it "sees" black or a white/reflective area
    def __init__(self):
        self.sensor = DInD(GPIO_PIN)
        self.max_frequency = MAX_FREQUENCY

    def get_color(self):
        return "White" if self.sensor.value == 1 else "Black"
    
    def get_color_existence(self):
        return self.sensor.value
 
    def read_data(self):
        value = self.sensor.value
        data = {
            "object_detection": value,
            "color": "White" if value == 1 else "Black"
        }
        return data

    def get_max_freq(self):
        return self.max_frequency

    def disconnect(self):
        #Release used resources
        self.sensor.close()

class TCRT5000(TrackerSensor):
    pass

class HW006(TrackerSensor):
    pass
import time
import adafruit_tfmini   
import serial

PORT = "/dev/ttyAMA0"
MAX_DISTANCE = 200.0
MIN_DISTANCE = 0.1
MAX_FREQUENCY = 100.0

class TFMini:
    def __init__(self):
        self.uart = serial.Serial(PORT, timeout=1)
        self.tfmini = adafruit_tfmini.TFmini(self.uart, timeout =60)
        self.max_distance = MAX_DISTANCE
        self.min_distance = MIN_DISTANCE
        self.max_frequency = MAX_FREQUENCY

    def read_data(self):
        data = {
            "distance": self.tfmini.distance,
           # "signal_strength": self.tfmini.strength,
           # "mode": self.tfmini.mode,
            "max_distance": self.max_distance,
            "min_distance": self.min_distance
        }
        return data
    
    def get_max_freq(self):
        return self.max_frequency    

    def disconnect(self):
        pass
import time
import adafruit_tfmini   
import serial

class TFMini:
    def __init__(self, port = "/dev/ttyAMA0"):
        self._uart = serial.Serial(port, timeout=1) 
        self._tfmini = adafruit_tfmini.TFmini(self._uart, timeout =60)

    def read_sensor(self):
        return {
            "distance": self._tfmini.distance,
            "strength": self._tfmini.strength,
            "mode": self._tfmini.mode
        }

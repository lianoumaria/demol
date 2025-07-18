import time
import board
import adafruit_vl53l1x

SENSOR_ADDRESS = 29
DISTANCE_MODE = 1
TIMING_BUDGET = 100
MAX_DISTANCE = 300.0
MIN_DISTANCE = 0.0
MAX_FREQUENCY = 50.0

class VL53L1X:
    def __init__(self):
        i2c = board.I2C()
        self.vl53 = adafruit_vl53l1x.VL53L1X(i2c, address = SENSOR_ADDRESS)
        self.vl53.distance_mode = DISTANCE_MODE
        self.vl53.timing_budget = TIMING_BUDGET
        self.vl53.start_ranging()
        self.open_sensor()
        self.max_distance = MAX_DISTANCE
        self.min_distance = MIN_DISTANCE
        self.max_frequency = MAX_FREQUENCY
    
    def read_data(self):
        if self.vl53.data_ready:
            data = {
                    "sensor_name": self.__class__.__name__,
                    "max_distance": self.max_distance,
                    "min_distance": self.min_distance,
                    "distance": self.vl53.distance
            }
            return data
        
    def get_max_freq(self):
        return self.max_frequency
    
    def disconnect(self):
        pass
import time
import board
#import digitalio # This is needed in case i decide to add XSHUT
import adafruit_vl53l1x

class VL53L1X:
    def __init__(self, slave_address = 0x29 , sens_distance_mode = 1, sens_timing_budget = 100):
        i2c = board.I2C()
        self.vl53 = adafruit_vl53l1x.VL53L1X(i2c, address = slave_address)
        self.vl53.distance_mode = sens_distance_mode
        self.vl53.timing_budget = sens_timing_budget
 
    def read_sensor(self):
        self.vl53.start_ranging()
        self.open_sensor()
        if self.vl53.data_ready:
            return self.vl53.distance

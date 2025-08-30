from ADCDifferentialPi import ADCDifferentialPi as ADCimported
import time

#Get the value from the device, else leave it as it is.
PGA = 1.0
BIT_MODE = 18.0
CHANNEL = 8.0 #Same as above
PRIMARY_SLAVE_ADDRESS = 0x68
SECONDARY_SLAVE_ADDRESS = 0x69
MAX_FREQUENCY = 240

class DifferentialADC:
    def __init__(self):
        self.adc = ADCimported(PRIMARY_SLAVE_ADDRESS, SECONDARY_SLAVE_ADDRESS)
        self.adc.set_pga(PGA)
        self.adc.set_bit_mode(BIT_MODE)
        self.max_frequency = MAX_FREQUENCY
    
    def read_data(self):
        voltage = self.adc.read_voltage(channel=CHANNEL)
        data = {"voltage": voltage}
        return data

    def get_max_freq(self):
        return self.max_frequency

    def disconnect(self):
        pass

class ADCDifferentialPi(DifferentialADC):
    pass
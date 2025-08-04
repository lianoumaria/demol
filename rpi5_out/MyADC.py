from ADCDifferentialPi import ADCDifferentialPi as ADCimported
import time

#Get the value from the device, else leave it as it is.
PGA = [1, 2, 4, 8]
BIT_MODE = [12, 14, 16, 18]
CHANNEL = 1 #Same as above
PRIMARY_SLAVE_ADDRESS = 0x68
SECONDARY_SLAVE_ADDRESS = 0x69

class DifferentialADC:
    def __init__(self):
        self.adc = ADCimported(PRIMARY_SLAVE_ADDRESS, SECONDARY_SLAVE_ADDRESS)
        self.adc.set_pga(PGA)
        self.adc.set_bit_mode(BIT_MODE)
    
    def read_data(self):
        voltage = self.adc.read_voltage(channel=CHANNEL)
        return voltage
    
    def disconnect(self):
        pass

class ADCDifferentialPi(DifferentialADC):
    pass
# It works inside a virtual environment
# The official page: https://github.com/pimoroni/bme680-python has details for it
import bme680
import time

DEFAULT_PRIMARY = bme680.I2C_ADDR_PRIMARY
DEFAULT_SECONDARY = bme680.I2C_ADDR_SECONDARY
PRIMARY_SLAVE_ADDRESS = 0x76
SECONDARY_SLAVE_ADDRESS = 0x77
MAX_FREQUENCY = 20

class BME680:
    # i don't know if it'll be possible to enter all these in the model
    def __init__(self):
        # Initiallize sensor
        '''
        try:
            self.sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
        except (RuntimeError, IOError):
            self.sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
        '''
        try:
            self.sensor = bme680.BME680(PRIMARY_SLAVE_ADDRESS)
        except (RuntimeError, IOError):
            self.sensor = bme680.BME680(SECONDARY_SLAVE_ADDRESS)

        #Initiallizing parameters
        self.sensor.set_humidity_oversample(bme680.OS_2X)
        self.sensor.set_pressure_oversample(bme680.OS_4X)
        self.sensor.set_temperature_oversample(bme680.OS_8X)
        self.sensor.set_filter(bme680.FILTER_SIZE_3)

        self.sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
        self.sensor.set_gas_heater_temperature(320)
        self.sensor.set_gas_heater_duration(150)
        self.sensor.select_gas_heater_profile(0)

        self.max_frequency = MAX_FREQUENCY
    
    def read_data(self):
        data = {}
        try:
            if self.sensor.get_sensor_data():
                data = {"temperature": self.sensor.data.temperature,
                             "pressure": self.sensor.data.pressure,
                             "humidity": self.sensor.data.humidity}
                if self.sensor.data.heat_stable:
                    data["gas_resistance"] = self.sensor.data.gas_resistance
                else:
                    data["gas_resistance"] = "Unstable heat, gas resistance not meassured"
            return data
        except KeyboardInterrupt:
            pass

    def get_max_frequency(self):
        return self.max_frequency    
    
    def disconnect(self):
        pass
    

        
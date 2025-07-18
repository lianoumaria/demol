# It works inside a virtual environment
# The official page: https://github.com/pimoroni/bme680-python has details for it
import bme680
import time

class BME680:
    # i don't know if it'll be possible to enter all these in the model
    #def __init__(self, hum_os, pres_os, temp_os, filter_size, gas_status, ):
    def __init__(self):
        # Initiallize sensor
        try:
            self.sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
        except (RuntimeError, IOError):
            self.sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

        #Initiallizing parameters
        self.sensor.set_humidity_oversample(bme680.OS_2X)
        self.sensor.set_pressure_oversample(bme680.OS_4X)
        self.sensor.set_temperature_oversample(bme680.OS_8X)
        self.sensor.set_filter(bme680.FILTER_SIZE_3)

        self.sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
        self.sensor.set_gas_heater_temperature(320)
        self.sensor.set_gas_heater_duration(150)
        self.sensor.select_gas_heater_profile(0)
    
    def temperature(self):
        try:
            while True:
                if self.sensor.get_sensor_data():
                    output = '{0:.2f}'.format(
                        self.sensor.data.temperature)
                    #Here i can only add a print and not a return.
                    #For return i should remove the while.
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    def pressure(self):
        try:
            while True:
                if self.sensor.get_sensor_data():
                    output = '{0:.2f}'.format(
                        self.sensor.data.pressure)
                    #Here i can only add a print and not a return
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    def humidity(self):
        try:
            while True:
                if self.sensor.get_sensor_data():
                    output = '{0:.2f}'.format(
                        self.sensor.data.humidity)
                    #Here i can only add a print and not a return
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    def gasResistance(self):
        try:
            while True:
                if self.sensor.get_sensor_data():
                    if self.sensor.data.heat_stable:
                        output = '{0},{1} Ohms'.format(
                            self.sensor.data.gas_resistance)
                        #Here i can only add a print and not a return
                    else:
                        print("Nothing yet")
        except KeyboardInterrupt:
            pass

    def getAll(self):
        try:
            while True:
                if self.sensor.get_sensor_data():
                    output = '{0:.2f} C,{1:.2f} hPa,{2:.2f} %RH'.format(
                        self.sensor.data.temperature,
                        self.sensor.data.pressure,
                        self.sensor.data.humidity)

                    if self.sensor.data.heat_stable:
                        print('{0},{1} Ohms'.format(
                            output,
                            self.sensor.data.gas_resistance))

                    else:
                        print(output)

                time.sleep(1)

        except KeyboardInterrupt:
            pass

    def airQuality(self, burnin_time):
        start_time = time.time()
        curr_time = time.time()
        burn_in_time = burnin_time

        burn_in_data = []

        try:
    # Collect gas resistance burn-in values, then use the average
    # of the last 50 values to set the upper limit for calculating
    # gas_baseline.
            while curr_time - start_time < burn_in_time:
                curr_time = time.time()
                if self.sensor.get_sensor_data() and self.sensor.data.heat_stable:
                    gas = self.sensor.data.gas_resistance
                    burn_in_data.append(gas)
                    print('Gas: {0} Ohms'.format(gas))
                    time.sleep(1)

            gas_baseline = sum(burn_in_data[-50:]) / 50.0

    # Set the humidity baseline to 40%, an optimal indoor humidity.
            hum_baseline = 40.0

    # This sets the balance between humidity and gas reading in the
    # calculation of air_quality_score (25:75, humidity:gas)
            hum_weighting = 0.25

            while True:
                if self.sensor.get_sensor_data() and self.sensor.data.heat_stable:
                    gas = self.sensor.data.gas_resistance
                    gas_offset = gas_baseline - gas

                    hum = self.sensor.data.humidity
                    hum_offset = hum - hum_baseline

            # Calculate hum_score as the distance from the hum_baseline.
                    if hum_offset > 0:
                        hum_score = (100 - hum_baseline - hum_offset)
                        hum_score /= (100 - hum_baseline)
                        hum_score *= (hum_weighting * 100)

                    else:
                        hum_score = (hum_baseline + hum_offset)
                        hum_score /= hum_baseline
                        hum_score *= (hum_weighting * 100)

            # Calculate gas_score as the distance from the gas_baseline.
                    if gas_offset > 0:
                        gas_score = (gas / gas_baseline)
                        gas_score *= (100 - (hum_weighting * 100))

                    else:
                        gas_score = 100 - (hum_weighting * 100)

            # Calculate air_quality_score.
                    air_quality_score = hum_score + gas_score

                    print('Gas: {0:.2f} Ohms,humidity: {1:.2f} %RH,air quality: {2:.2f}'.format(
                        gas,
                        hum,
                        air_quality_score))

                    time.sleep(1)

        except KeyboardInterrupt:
            pass


    def read_data(self):
        if self.sensor.get_sensor_data():
            data = {
                "temperature": self.sensor.data.temperature,
                "pressure": self.sensor.data.pressure,
                "humidity": self.sensor.data.humidity
            }

            if self.sensor.data.heat_stable:
                data["gas_resistance"] = self.sensor.data.gas_resistance

            return data  

        


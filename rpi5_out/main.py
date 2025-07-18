
from demol.templates.raspi_new.sensor_classes.TrackerClass import TCRT5000
from demol.templates.raspi_new.sensor_classes.DistanceClass import SRF05

from demol.templates.raspi_new.sensor_classes import VL53L1X

from demol.templates.raspi_new.sensor_classes import TFMini

from demol.templates.raspi_new.sensor_classes import BME680


# Example usage:
def main():

# Αργότερα αν προχωρήσω ίσως δημιουργώ threads στη λούπα
    
    MyTracker = TCRT5000("GPIO4")
    data_MyTracker = MyTracker.read_sensor()
    MySRF = SRF05(trigger = "GPIO23", echo = "GPIO24")
    data_MySRF = MySRF.read_sensor()
    MyToF = VL53L1X(slave_address = 29)
    data_MyToF = MyToF.read_sensor()
    MyTFMini = TFMini("/dev/ttyAMA0")
    data_MyTFMini = MyTFMini.read_sensor()
    MyBME = BME680()
    data_MyBME = MyBME.read_sensor()
    

if __name__ == "__main__":
    main()
# servo classes are defined considering a pca9685 servo driver
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import numpy as np
import board
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

FREQUENCY = 50  # Frequency for the PCA9685
CHANNEL = 2.0 
INITIAL_ANGLE = 90.0  # Initial angle for the servo
FINAL_ANGLE = 180.0  # Final angle for the servo
ANGULAR_SPEED = 0.5  # Speed of the servo movement in degrees per second
ANGULAR_STEP = 1  # Step size for the servo movement in degrees
MAX_FREQUENCY = 1000
MIN_PULSE = 500
MAX_PULSE = 2500

class ServoClass:
    def __init__(self):
        self.i2c = board.I2C()
        self.pca = PCA9685(self.i2c)
        if FREQUENCY >= MAX_FREQUENCY:
            raise ValueError(f"Frequency {FREQUENCY} Hz exceeds maximum {MAX_FREQUENCY} Hz.")
        self.pca.frequency = FREQUENCY
        self.servo7 = servo.Servo(self.pca.channels[CHANNEL], min_pulse=MIN_PULSE, max_pulse=MAX_PULSE)
    

    def set_action(self):
        angle_range = np.arange(INITIAL_ANGLE, FINAL_ANGLE + ANGULAR_STEP, ANGULAR_STEP)
        speed = ANGULAR_SPEED / ANGULAR_STEP  # Speed in seconds per step
        for angle in angle_range:
            self.servo7.angle = angle
            time.sleep(speed)

    def disconnect(self):
        self.pca.deinit()

class MG996R_PCA9685(ServoClass):
    pass
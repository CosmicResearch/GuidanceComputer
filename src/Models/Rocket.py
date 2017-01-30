"""
    Guidance Computer Software
    Copyright (C) 2016 Associacio Cosmic Research

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import ConfigParser
import math
import time
from Models import SensorData
import RPi.GPIO as GPIO

class Rocket:

    """
    This class represents the rocket's main logic.
    """

    def __init__(self, config_file):
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        self.main_open_altitude = int(config.get("Rocket", "MainOpenAltitude"))
        self.main_pin = int(config.get("Rocket", "MainPin"))
        self.drogue_pin = int(config.get("Rocket", "DroguePin"))
        self.number_reads = int(config.get("Rocket", "NumberOfReads"))
        self.lift_off_altitude = int(config.get("Rocket", "LiftOffAltitude"))
        self.nreads = self.number_reads
        self.launch_data = None
        self.last_data = None
        self.current_data = None
        self.drogue_fired = False
        self.main_fired = False
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.drogue_pin, GPIO.OUT)
        GPIO.output(self.drogue_pin, GPIO.HIGH)
        GPIO.setup(self.main_pin, GPIO.OUT)
        GPIO.output(self.main_pin, GPIO.HIGH)

    def update_values(self, values):
        """
        Updates the sensors readings and performs the corresponding
        actions.
        """
        if not self.launch_data:
            self.launch_data = SensorData.SensorData.copy(values)
            self.current_data = SensorData.SensorData.copy(values)
            self.current_data.altitude = 0
        else:
            self.last_data = self.current_data
            self.current_data = SensorData.SensorData.copy(values)
            self.current_data.altitude = Rocket.nearest_int(self.current_data.altitude - self.launch_data.altitude)
            self.chute_logic()

    def chute_logic(self):
        """
        Checks if we should open any of the chutes
        """
        if not self.is_in_mach_speed():
            if self.current_data.altitude > self.lift_off_altitude and not self.main_fired and not self.drogue_fired:
                if self.current_data.altitude < self.last_data.altitude:
                    self.nreads -= 1
                    if self.nreads == 0:
                        self.open_drogue()
                elif self.current_data.altitude > self.last_data.altitude:
                    self.nreads = self.number_reads
            if self.current_data.altitude <= self.main_open_altitude and self.drogue_fired and not self.main_fired:
                self.open_main()

    def open_drogue(self):
        """
        This method will attempt to open the drogue chute.
        """
        GPIO.output(self.drogue_pin, GPIO.LOW)
        self.drogue_fired = True
        time.sleep(20.0/1000.0)
        GPIO.output(self.drogue_pin, GPIO.HIGH)


    def open_main(self):
        """
        This method will attempt to open the drogue chute.
        """
        GPIO.output(self.main_pin, GPIO.LOW)
        self.main_fired = True
        time.sleep(20.0/1000.0)
        GPIO.output(self.main_pin, GPIO.HIGH)

    @staticmethod
    def nearest_int(number):
        """
        Converts a floating point number to its nearest integer
        """
        number_up = math.ceil(number)
        number_down = math.floor(number)
        if number < number_down+0.5:
            return number_down
        else:
            return number_up

    def is_in_mach_speed(self):
        """
        Determines if the Rocket is in Mach speed based on the velocity
        and the altitude.
        """
        mach_speeds = [
            (0, 340.3),
            (1524, 334.4),
            (3048, 328.4),
            (4572, 322.2),
            (6096, 316.0),
            (7620, 309.6),
            (9144, 303.1),
            (10668, 295.4),
            (12192, 294.9)
        ]
        speed = 0
        for key, value in mach_speeds:
            if key <= self.current_data.altitude:
                speed = value
            elif key >= self.current_data.altitude and key-762 <= self.current_data.altitude:
                speed = value
                break
            else:
                break
        return self.current_data.velocity > 0.8*speed

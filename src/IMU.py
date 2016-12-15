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

from multiprocessing import Process
import time
import math
import sys
import traceback
import RTIMU
import RPi.GPIO as GPIO
from constants import *


class IMUProcess(Process):

    """
    This class represents the rocket logic, all sensors should be read here
    and all the actions should be taken here (like launching the chutes).
    """

    def __init__(self, queue):
        Process.__init__(self)
        self.name = "IMUProcess"
        self.daemon = True
        self.queue = queue
        self.poll_rate = 0.0
        self._t0 = time.clock()
        self.config_file = RTIMU.Settings("RTIMULib")
        self.imu = RTIMU.RTIMU(self.config_file)
        self.pressure = RTIMU.RTPressure(self.config_file)
        self.drogue_fired = False
        self.main_fired = False
        self.last_data = 0, (0, 0, 0)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(DROGUE_PIN, GPIO.OUT)
        GPIO.output(DROGUE_PIN, GPIO.LOW)
        GPIO.setup(MAIN_PIN, GPIO.OUT)
        GPIO.output(MAIN_PIN, GPIO.LOW)

    def run(self):
        self._t0 = time.clock()
        try:
            altitude_launch = self.init_sensors()
        except IMUException as exception:
            self.log_error(exception.args.__repr__())
            return
        old_altitude = 0
        nreads = NUMBER_READS
        while True:
            self.correct_sleep(self.poll_rate)
            data = self.read_sensors()
            self.last_data = data[1], data[2]
            self.queue.put(data)
            altitude = IMUProcess.nearest_int(data[1]) - altitude_launch
            if altitude > LIFTOFF_ALTITUDE and not self.main_fired and not self.main_fired:
                if altitude < old_altitude:
                    nreads -= 1
                    if nreads == 0:
                        GPIO.output(DROGUE_PIN, GPIO.HIGH)
                        self.drogue_fired = True
                        self.correct_sleep(20.0/1000.0)
                        GPIO.output(DROGUE_PIN, GPIO.LOW)
                elif altitude > old_altitude:
                    nreads = NUMBER_READS
            if altitude <= MAIN_ALTITUDE and not self.main_fired and self.drogue_fired:
                GPIO.output(MAIN_PIN, GPIO.HIGH)
                self.main_fired = True
                self.correct_sleep(20.0/1000.0)
                GPIO.output(MAIN_PIN, GPIO.LOW)
            old_altitude = altitude

    def terminate(self):
        self.queue.close()
        Process.terminate(self)

    def init_sensors(self):
        """
        Initialises and configures the IMU and the pressure sensor
        also sets the recommended poll_rate and the lauch altitude
        """
        if not self.imu.IMUInit():
            print("IMUInit failed")
            raise IMUException("IMUInit failed")
        if not self.pressure.pressureInit():
            print("PressureInit failed")
            raise IMUException("PressureInit failed")
        self.imu.setGyroEnable(True)
        self.imu.setAccelEnable(True)
        self.imu.setCompassEnable(True)
        self.imu.setSlerpPower(0.02)
        self.poll_rate = float(float(self.imu.IMUGetPollInterval())/1000.0)
        altitude_launch = self.read_sensors()[1]
        while altitude_launch == 0:
            self.correct_sleep(self.poll_rate)
            altitude_launch = self.read_sensors()[1]
        print(time.clock() - self._t0, altitude_launch)
        return IMUProcess.nearest_int(altitude_launch)

    def read_sensors(self):
        """
        If the reading from the IMU and the presure sensor was succesful,
             returns all the readings from the IMU
        The readings are returned in a tuple as (time, altitude, orientation):
            time: the delta time since self._t0 was set -> float
            altitude: the absolute current altitude mesured with the pressure
                from the pressure sensor -> float
            orientation: current orientation as Euler angles (roll, pitch, yaw) -> tuple
                pitch: angle between the IMU and the lateral axis -> float
                roll: angle between the IMU and the logintudinal axis -> float
                yaw: angle between the IMU and the perpendicular axis -> float

        If the reading from the IMU or the pressure sensor was not succesful,
        the last correct reading is returned Although it may sound strange,
        it is the correct approach as no action is performed if the relative altitude
        remains the same.
        """
        if self.imu.IMURead():
            data = self.imu.getIMUData()
            data["pressureValid"], data["pressure"], data["temperatureValid"], data["temperature"] = self.pressure.pressureRead()
            if data["pressureValid"]:
                altitude = IMUProcess.compute_height(data["pressure"])
            else:
                self.log_error("Pressure not valid")
                return time.clock() - self._t0, self.last_data[0], self.last_data[1]
            orientation = data["fusionPose"]
            roll = math.degrees(orientation[0])
            pitch = math.degrees(orientation[1])
            yaw = math.degrees(orientation[2])
            return time.clock() - self._t0, altitude, (roll, pitch, yaw)
        else:
            self.log_error("Cant read from IMU")
            return time.clock() - self._t0, self.last_data[0], self.last_data[1]

    def correct_sleep(self, sleep_time):
        """
        Sleeps the thread for sleep_time seconds.
        We have tested on a RPi 3 that time.sleep(sleep_time) with sleep_time < 0 will not
        sleep for sleep_time but for a random time. According to the documentation this should
        not happen.
        """
        delta_time = 0
        before_sleep = time.clock()
        while delta_time < sleep_time:
            time.sleep(sleep_time - delta_time)
            delta_time = time.clock() - before_sleep

    @staticmethod
    def compute_height(pressure):
        """
        Returns the altitude as a float based on the current air pressure

        The altitude is calculated based on a formula published by NOAA, the
        original formula converts milibars to feets, but it can be adapted
        to SI units.
        """
        return 44330.8 * (1 - pow(pressure / 1013.25, 0.190263))

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

    def log_error(self, msg):
        """
        Logs an error ocurred when interacting with the IMU
        """
        exception_file = open("log_error.txt", mode='a')
        exception_file.write("** {0} IMUError: {1}\n".format(time.clock() - self._t0, msg))
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_type and exc_value and exc_traceback:
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            exception_file.write(''.join('!! ' + line for line in lines))
        exception_file.close()

class IMUException(Exception):
    """
    Represents an Exception ocurred when interacting with the IMU
    """
    pass

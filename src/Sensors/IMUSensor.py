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

import time
import math
import RTIMU
from Models import SensorData
from Exceptions import IMUException
from Sensors import SensorBase

class IMUSensor(SensorBase.SensorBase):

    """
    This class represents the sensor fusion. This class, reads,
    preprocess all the sensor data and returns it.
    """

    def __init__(self):
        self.imu = None
        self.pressure = None
        self.poll_rate = 0.0
        self.last_data = None
        self.current_data = None
        self.callback = None


    def init_sensor(self):
        config_file = RTIMU.Settings("RTIMULib")
        self.imu = RTIMU.RTIMU(config_file)
        self.pressure = RTIMU.RTPressure(config_file)
        if not self.imu.IMUInit():
            #print("IMUInit failed")
            raise IMUException.IMUException("IMUInit failed")
        if not self.pressure.pressureInit():
            #print("PressureInit failed")
            raise IMUException.IMUException("PressureInit failed")
        self.imu.setGyroEnable(True)
        self.imu.setAccelEnable(True)
        self.imu.setCompassEnable(True)
        self.imu.setSlerpPower(0.02)
        self.poll_rate = float(float(self.imu.IMUGetPollInterval())/1000.0)
        self.current_data = SensorData.SensorData(time=time.time())
        self.current_data.altitude = 0
        while self.current_data.altitude == 0:
            time.sleep(self.poll_rate)
            try:
                self.read(checks=False)
            except IMUException.IMUException:
                pass
        self.last_data = self.current_data

    def read(self, new_data=None, checks=True):
        trying = True
        attempts = 100
        while trying:
            if not self.imu.IMURead():
                attempts -= 1
                if attempts == 50:
                    self.init_sensor()
                if attempts == 0:
                    trying = False
            else:
                trying = False
        if attempts == 0:
            raise IMUException.IMUException("Cant read from IMU")
            print("Cant read from imu")
        return self._read(new_data, checks)

    def _read(self, data=None, checks=True):
        imu_data = self.imu.getIMUData()
        pressure_data = self.pressure.pressureRead()
        if not pressure_data[0] and checks:
            raise IMUException.IMUException("Pressure not valid")
        if (not imu_data["accelValid"] or not imu_data["compassValid"] or not imu_data["gyroValid"]) and checks:
            raise IMUException.IMUException("IMU Readings not valid")
        self.last_data = self.current_data
        if data:
            self.current_data = SensorData.SensorData.copy(data)
            self.current_data.time = time.time()
        else:
            self.current_data = SensorData.SensorData(time=time.time())
        if pressure_data[0]:
            self.current_data.altitude = self.compute_height(pressure_data[1])
            self.current_data.pressure = pressure_data[1]
            self.current_data.temperature = pressure_data[3]
        else:
            self.current_data.altitude = 0
            self.current_data.pressure = pressure_data[1]
            self.current_data.temperature = pressure_data[3]
        orientation = imu_data["fusionPose"]
        roll = math.degrees(orientation[0])
        pitch = math.degrees(orientation[1])
        yaw = math.degrees(orientation[2])
        self.current_data.orientation = {"roll": roll, "pitch": pitch, "yaw": yaw}
        acceleration = imu_data["accel"]
        self.current_data.acceleration = (acceleration[0], acceleration[1], acceleration[2])
        gyro = imu_data["gyro"]
        self.current_data.gyro = (gyro[0], gyro[1], gyro[2])
        compass = imu_data["compass"]
        self.current_data.compass = (compass[0], compass[1], compass[2])
        self.current_data.velocity = self.compute_velocity()
        if self.callback:
            self.callback(self.current_data)
        else:
            return self.current_data

    def set_read_callback(self, callback):
        self.callback = callback

    def compute_velocity(self):
        """
        Computes the velocity given two readings, last_reading and current_reading
        The velocity is approximated given the current acceleration and the delta time
        """
        if self.last_data and self.last_data.acceleration and self.last_data.time:
            accel = self.current_data.acceleration
            accel = math.sqrt((accel[0]**2) + (accel[1]**2) + (accel[2]**2))
            return self.last_data.velocity + accel*(self.current_data.time - self.last_data.time)
        else:
            return 0

    def compute_height(self, pressure):
        """
        Returns the altitude as a float based on the current air pressure
        The altitude is calculated based on a formula published by NOAA, the
        original formula converts milibars to feets, but it can be adapted
        to SI units.
        """
        return 44330.8 * (1 - pow(pressure / 1013.25, 0.190263))

    def correct_sleep(self, sleep_time):
        """
        Sleeps the thread for sleep_time seconds.
        We have tested on a RPi 3 that time.sleep(sleep_time) with 0 <= sleep_time <= 1 will not
        sleep for sleep_time but for a random time. According to the documentation this should
        not happen.
        """
        delta_time = 0
        before_sleep = time.time()
        while delta_time < sleep_time:
            time.sleep(sleep_time - delta_time)
            delta_time = time.time() - before_sleep


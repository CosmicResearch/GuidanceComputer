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

from multiprocessing import Process, Queue
import time
import RTIMU
import math


class IMUProcess(Process):
    def __init__(self, queue):
        Process.__init__(self)
        self.name = "IMUProcess"
        self.daemon = True
        self.queue = queue
        self.poll_rate = 0.0  # In seconds
        self._t0 = time.time()
        self.config_file = RTIMU.Settings("settings.ini")
        self.imu = RTIMU.RTIMU(self.config_file)
        self.pressure = RTIMU.RTPressure(self.config_file)

    def run(self):
        try:
            self.init_sensors()
        except SensorError as e:
            print("SensorError: ", e)
            while True: pass
        self._t0 = time.time()
        while True:
            try:
                data = self.read_sensors()
                self.queue.put(data)
            except SensorError as error:
                print("SensorError: ", error)
            time.sleep(self.poll_rate)

    def terminate(self):
        self.queue.close()
        Process.terminate(self)

    def init_sensors(self):
        if not self.imu.IMUInit():
            raise SensorError("IMUInit failed")
        if not self.pressure.pressureInit():
            raise SensorError("PressureInit failed")
        self.imu.setGyroEnable(True)
        self.imu.setAccelEnable(True)
        self.imu.setCompassEnable(True)
        self.imu.setSlerpPower(0.02)
        self.poll_rate = self.imu.IMUGetPollInterval()

    def read_sensors(self):
        if self.imu.IMURead():
            data = self.imu.getIMUData()
            (data["pressureValid"], data["pressure"], data["temperatureValid"], data["temperature"]) = self.pressure.pressureRead()
            if data["pressureValid"]:
                altitude = IMUProcess.compute_height(data["pressure"])
            else:
                raise SensorError("Pressure not valid!")
            orientation = data["fusionPose"]
            roll = math.degrees(orientation[0])
            pitch = math.degrees(orientation[1])
            yaw = math.degrees(orientation[2])
            return time.time() - self._t0, altitude, (roll, pitch, yaw) # time, altitude, orientation (r,p,y)
        else:
            raise SensorError("Can't read from IMU")

    @staticmethod
    def compute_height(pressure):
        return 44330.8 * (1 - pow(pressure / 1013.25, 0.190263))


class SensorError(Exception):
    pass

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
import RPi.GPIO as GPIO


class IMUProcess(Process):
    def __init__(self, queue):
        Process.__init__(self)
        self.name = "IMUProcess"
        self.daemon = True
        self.queue = queue
        self.poll_rate = 0.0  # In seconds
        self._t0 = time.time()
        self.config_file = RTIMU.Settings("settings")
        self.imu = RTIMU.RTIMU(self.config_file)
        self.pressure = RTIMU.RTPressure(self.config_file)
        self.nreads = 10
        self.liftoff_altitude = 20
        self.drogue_fired = False
        self.main_fired = False
        self.main_pin = 18
        self.drogue_pin = 17
        self.main_altitude = 200
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.drogue_pin, GPIO.OUT)
        GPIO.output(self.drogue_pin, GPIO.LOW)
        GPIO.setup(self.main_pin, GPIO.OUT)
        GPIO.output(self.main_pin, GPIO.LOW)

    def run(self):
        old_altitude = 0
        nreads = self.nreads
        self.init_sensors()
        self._t0 = time.time()
        while True:
            data = self.read_sensors()
            self.queue.put(data)
            altitude = IMUProcess.nearest_int(data[1])
            print("altitude: " + str(altitude))
            if altitude > self.liftoff_altitude and not self.main_fired and not self.main_fired:
                if altitude < old_altitude:
                    nreads -= 1
                    if nreads == 0:
                        GPIO.output(self.drogue_pin, GPIO.HIGH)
                        self.drogue_fired = True
                        time.sleep(20/1000)
                        GPIO.output(self.drogue_pin, GPIO.LOW)
                elif altitude > old_altitude:
                    nreads = self.nreads
            if altitude <= self.main_altitude and not self.main_fired and self.drogue_fired:
                GPIO.output(self.main_pin, GPIO.HIGH)
                self.main_fired = True
                time.sleep(20/1000)
                GPIO.output(self.main_pin, GPIO.LOW)
            old_altitude = altitude
            time.sleep(self.poll_rate)

    def terminate(self):
        self.queue.close()
        Process.terminate(self)

    def init_sensors(self):
        if not self.imu.IMUInit():
            print("IMUInit failed")
        if not self.pressure.pressureInit():
            print("PressureInit failed")
        self.imu.setGyroEnable(True)
        self.imu.setAccelEnable(True)
        self.imu.setCompassEnable(True)
        self.imu.setSlerpPower(0.02)
        self.poll_rate = self.imu.IMUGetPollInterval()/1000

    def read_sensors(self):
        if self.imu.IMURead():
            data = self.imu.getIMUData()
            (data["pressureValid"], data["pressure"], data["temperatureValid"], data["temperature"]) = self.pressure.pressureRead()
            if data["pressureValid"]:
                altitude = IMUProcess.compute_height(data["pressure"])
            else:
                print("Pressure not valid")
                return
            orientation = data["fusionPose"]
            roll = math.degrees(orientation[0])
            pitch = math.degrees(orientation[1])
            yaw = math.degrees(orientation[2])
            return time.time() - self._t0, altitude, (roll, pitch, yaw) # time, altitude, orientation (r,p,y)
        else:
            print("Cant read from IMU")
            return

    @staticmethod
    def compute_height(pressure):
        return 44330.8 * (1 - pow(pressure / 1013.25, 0.190263))

    @staticmethod
    def nearest_int(n):
        up = math.ceil(n)
        down = math.floor(n)
        if n < down+0.5:
            return down
        else:
            return up

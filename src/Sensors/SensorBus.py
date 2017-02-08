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
from threading import Thread, Lock, Event
import time
import sys
from Models import SensorData
from Exceptions import SensorException

class SensorBus:

    """
    This class represents a bus of sensors.
    This class lets you read a group of sensors in background.
    """

    def __init__(self, config_file):
        self.sensor_list = []
        self.read_callback = None
        self.error_callback = None
        self.thread_lock = Lock()
        self.running = True
        self.thread = None
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        self.poll_rate = float(config.get("Sensors", "PollRate"))/1000.0

    def set_read_callback(self, callback):
        """
        Sets the callback to call when all the sensors
        have been read.
        """
        self.read_callback = callback

    def set_error_callback(self, callback):
        """
        Sets the callback to call when an Error or Exception
        is occurred when interacting with a sensor
        """
        self.error_callback = callback

    def start_reading(self):
        """
        Starts reading the sensors in background
        Returns if the reading was started or not
        """
        if self.thread_lock.acquire(False):
            self.thread = Thread(target=self._read_loop)
            self.thread.start()
            return True
        return False

    def stop_reading(self):
        """
        Stops reading the sensors
        """
        if self.thread and self.thread.is_alive():
            self.running = False

    def _read_loop(self):
        while self.running:
            time.sleep(self.poll_rate)
            data = SensorData.SensorData()
            for sensor in self.sensor_list:
                try:
                    sensor.read(new_data=data)
                except SensorException.SensorException as exception:
                    self.error_callback(exception)
                data = sensor.current_data
            self.read_callback(data)

    def register_sensor(self, sensor):
        """
        Registers a new sensor to be read.
        """
        try:
            sensor.init_sensor()
        except SensorException.SensorException as exception:
            self.error_callback(exception)
        self.sensor_list.append(sensor)

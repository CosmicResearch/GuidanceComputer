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
from gps import *
from Sensors import SensorBase
from threading import Thread
from Models import SensorData

class GPSSensor(SensorBase.SensorBase, Thread):

    def __init__(self, ):
        Thread.__init__(self)
        self.current_data = None
        self.last_data = None
        self.callback = None
        self.thread_running = False
        self.daemon = True
        self.report = None
        self.lat = 0.0
        self.lon = 0.0
        self.session = gps("localhost", "2947")
        self.session.stream(WATCH_ENABLE|WATCH_NEWSTYLE)

    def init_sensor(self):
        self.thread_running = True
        self.start()

    def read(self, new_data=None, checks=True):
        self.last_data = self.current_data
        if new_data:
            self.current_data = SensorData.SensorData.copy(new_data)
            self.current_data.time = time.time()
        else:
            self.current_data = SensorData.SensorData(time.time())
        self.current_data.latitude = self.lat
        self.current_data.longitude = self.lon
        if self.callback:
            self.callback(self.current_data)
        else:
            return self.current_data

    def run(self):
        """
        Polls the gps socket
        """
        try:
            while self.thread_running:
                self.report = self.session.next()
                try:
                    if self.report['class'] == 'DEVICE':
                        self.session.close()
                        self.session = gps(mode=WATCH_ENABLE)
                    v_lat = self.report["lat"]
                    v_lon = self.report["lon"]
                    self.lat = v_lat
                    self.lon = v_lon
                except KeyError:
                    pass
        except StopIteration:
            return

    def set_read_callback(self, callback):
        self.callback = callback

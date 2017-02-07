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

import os
from Communicators import CommunicatorBase
from Models import SensorData

class Logger(CommunicatorBase.CommunicatorBase):

    def __init__(self):
        self.data_file = None
        self.other_file = None
        self.writes = 0

    def init(self):
        offset = 0
        path = "./data"
        while os.path.exists(path+str(offset)):
            offset += 1
        self.data_file = open(path+str(offset), mode="a")
        offset = 0
        path = "./other"
        while os.path.exists(path+str(offset)):
            offset += 1
        self.other_file = open(path+str(offset), mode="a")

    def write(self, data):
        if isinstance(data, SensorData.SensorData):
            self.data_file.write(data.__repr__())
        else:
            self.other_file.write(data)
        self.writes += 1
        if self.writes >= 100:
            self.data_file.flush()
            self.other_file.flush()
            os.fsync(self.data_file.fileno())
            os.fsync(self.other_file.fileno())

    def read(self):
        return []

    def shutdown(self):
        self.data_file.close()
        self.other_file.close()
        
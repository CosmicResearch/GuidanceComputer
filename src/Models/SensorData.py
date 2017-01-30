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

class SensorData:

    """
    This class represents data returned by the
    sensor fusion.
    """

    def __init__(self, time=None):
        self.time = time
        self.temperature = None
        self.pressure = None
        self.altitude = None
        self.acceleration = ()
        self.gyro = ()
        self.orientation = {}
        self.compass = ()
        self.velocity = None
        self.latitude = None
        self.longitude = None

    @staticmethod
    def copy(data):
        """
        Creates a copy of a SensorData
        """
        copy = SensorData(data.time)
        copy.temperature = data.temperature
        copy.pressure = data.pressure
        copy.altitude = data.altitude
        copy.acceleration = data.acceleration
        copy.gyro = data.gyro
        copy.orientation = data.orientation
        copy.compass = data.compass
        copy.velocity = data.velocity
        return copy

    def __repr__(self):
        info = "{0}: temp:{1} press:{2} alt:{3} accel:{4} gyro:{5} or:{6} comp:{7} vel:{8} lat:{9} lon:{10}\n".format(self.time,
            self.temperature, self.pressure, self.altitude, self.acceleration, self.gyro, self.orientation, self.compass, 
            self.velocity, self.latitude, self.longitude)
        return info

    def __str__(self):
        return self.__repr__()
        
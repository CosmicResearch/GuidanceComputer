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

class SensorBase:

    def __init__(self):
        self.current_data = None
        self.last_data = None
        raise NotImplementedError()

    def init_sensor(self):
        """
        Initializes the sensor
        """
        raise NotImplementedError()

    def read(self, new_data=None, checks=True):
        '''
        Tells the sensor to read a new value.

        checks: boolean. if False, no checks will be performed to the readings

        new_data: SensorData. if not None, the sensor will populate it
                  instead of creating a new object
        '''
        raise NotImplementedError()

    def set_read_callback(self, callback):
        """
        Sets the callback to call when the read has ended succesfully.
        """
        raise NotImplementedError()

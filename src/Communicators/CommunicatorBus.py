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

class CommunicatorBus:

    def __init__(self, config_file):
        self.communicator_list = []

    def write(self, data):
        """
        Write data to all the communicators
        """
        for communicator in self.communicator_list:
            communicator.write(data)

    def register_communicator(self, communicator):
        """
        Register a new communicator
        """
        communicator.init()
        self.communicator_list.append(communicator)

    def read(self):
        """
        Reads updates from all the communicators
        """
        updates = []
        for communicator in self.communicator_list:
            updates += communicator.read()
        return updates

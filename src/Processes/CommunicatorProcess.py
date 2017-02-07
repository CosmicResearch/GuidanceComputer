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


from threading import Thread
from Communicators import CommunicatorBus
from Communicators import Logger, Printer, MSCommunicator


class CommunicatorProcess(Thread):

    """
    This class represents a communicator process.
    All the communications should be done here.
    """

    def __init__(self, queue_out, queue_in):
        Thread.__init__(self)
        self.name = "CommunicatorProcess"
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.daemon = True
        self.communicator_bus = CommunicatorBus.CommunicatorBus("./config.ini")
        self.communicator_bus.register_communicator(Logger.Logger())
        self.communicator_bus.register_communicator(MSCommunicator.RFMCommunicator())
        #self.communicator_bus.register_communicator(Printer.Printer())
        self.running = True

    def run(self):
        while self.running:
            inputs = self.communicator_bus.read()
            for data in inputs:
                self.queue_out.put(data)
            data = self.queue_in.get()
            self.communicator_bus.write(data)

    def stop(self):
        self.running = False
        self.communicator_bus.shutdown()


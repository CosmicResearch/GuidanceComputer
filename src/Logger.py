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


from multiprocessing import Process
import os
import time


class LoggerProcess(Process):

    """
    This class represents a datalogger process.
    All the datalogging (except for error logging) should be done here.
    """

    def __init__(self, queue):
        Process.__init__(self)
        self.name = "LoggerProcess"
        self.queue = queue
        self.daemon = True
        offset = 0
        path = "./data"
        while os.path.exists(path+str(offset)):
            offset += 1
        self.file = open(path+str(offset), mode="a")
        self._t0 = time.time()

    def run(self):
        nwrites = 0
        self._t0 = time.time()
        while True:
            data = self.queue.get()
            self.file.write("(" + str(data[0]) + "," + str(data[1])
                            + ",(" + str(data[2][0]) + "," + str(data[2][1])
                            + "," + str(data[2][2]) + "))\n")
            nwrites += 1
            if nwrites >= 10:
                self.file.flush()
                os.fsync(self.file.fileno())

    def terminate(self):
        self.file.flush()
        os.fsync(self.file.fileno())
        self.file.close()
        self.queue.close()
        Process.terminate(self)
        
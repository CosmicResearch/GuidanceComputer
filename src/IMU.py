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


class IMUProcess(Process):

    def __init__(self, queue):
        Process.__init__(self)
        self.name = "IMUProcess"
        self.daemon = True
        self.queue = queue
        self.poll_rate = 10/1000  # In seconds
        self._t0 = time.time()

    def run(self):
        self._t0 = time.time()
        while True:
            data = self.read_sensors()
            self.queue.put(data)
            time.sleep(self.poll_rate)

    def terminate(self):
        self.queue.close()
        Process.terminate(self)

    def read_sensors(self):
        return time.time() - self._t0, 100, (0, 0, 1)  # time, altitude, orientation

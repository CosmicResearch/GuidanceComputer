#! /usr/bin/env python

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

import Logger
import IMU
from multiprocessing import Lock, Process, Queue
import RPI.GPIO as GPIO

if __name__ == "__main__":
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(4, GPIO.OUT)
    GPIO.output(4, GPIO.HIGH)
    queue = Queue()
    LoggerProcess = Logger.LoggerProcess(queue)
    IMUProcess = IMU.IMUProcess(queue)
    LoggerProcess.start()
    IMUProcess.start()
    try:
        LoggerProcess.join()
        IMUProcess.join()
    except KeyboardInterrupt:
        LoggerProcess.terminate()
        IMUProcess.terminate()
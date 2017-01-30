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

import logging
import ConfigParser
from threading import Thread
from Sensors import IMUSensor, GPSSensor, SensorBus
from Models import Rocket
import RPi.GPIO as GPIO

class SensorProcess(Thread):

    """
    This class represents the rocket logic.
    """

    def __init__(self, queue_out, queue_in):
        Thread.__init__(self)
        self.name = "SensorProcess"
        self.daemon = True
        self.queue_out = queue_out
        self.queue_in = queue_in
        self.logger = logging.getLogger("sensor_logger")
        self.sensor_bus = SensorBus.SensorBus("./config.ini")
        self.sensor_bus.set_read_callback(self.on_read)
        self.sensor_bus.set_error_callback(self.on_error)
        self.sensor_bus.register_sensor(IMUSensor.IMUSensor())
        self.sensor_bus.register_sensor(GPSSensor.GPSSensor())
        self.rocket = Rocket.Rocket("./config.ini")
        handler = logging.FileHandler("./sensor_errors.log")
        config = ConfigParser.ConfigParser()
        config.read("./config.ini")
        self.ok_led_pin = int(config.get("LED", "OkLedPin"))
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.ERROR)
        self.running = True
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.ok_led_pin, GPIO.OUT)
        GPIO.output(self.ok_led_pin, GPIO.HIGH)


    def run(self):
        self.sensor_bus.start_reading()
        while self.running:
            order = self.queue_in.get(True)
            self.process_order(order)

    def on_read(self, reading):
        """
        Read callback
        """
        self.rocket.update_values(reading)
        self.queue_out.put(reading)

    def on_error(self, error):
        """
        Error callback
        """
        self.logger.error(error.args)

    def process_order(self, order):
        """
        Processes an order received by an external actor.
        TODO
        """
        if order == "ECHO":
            self.queue_out("AYY LMAO")

    def stop(self):
        self.sensor_bus.stop_reading()
        self.running = False
        GPIO.output(self.ok_led_pin, GPIO.LOW)

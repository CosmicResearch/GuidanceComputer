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

import struct
import time
from RFM69 import RFM69, RFM69registers
from Communicators import CommunicatorBase
from Models import SensorData

class RFMCommunicator(CommunicatorBase.CommunicatorBase):

    def __init__(self):
        # def __init__(self, freqBand, nodeID, networkID, isRFM69HW = False,
        #intPin = 18, rstPin = 29, spiBus = 0, spiDevice = 0):
        self.trans = RFM69.RFM69(RFM69registers.RFM69_433MHZ, 2, 2, True, 18, 29, 0, 0)
        # Set max power 20 dBm
        # self.trans.setPowerLevel(RF_PALEVEL_OUTPUTPOWER_11111) #done by default when initializing
        #self.trans.setHighPower(True)  #done by default when initializing
        #self.trans.setHighPowerRegs(False) #done by default when changeing to rx mode
        self.trans.rcCalibration()
        self.trans.receiveBegin() #Initialize parameters and set rx mode


    def read(self):
        data_recv = []
        if self.trans.receiveDone():
            if self.trans.ACKRequested():
                self.trans.sendACK()
            data_recv = self.trans.DATA
        #We really don't need this second part, but it's a good way to make
        #the transceiver stay a few time in silence
        elif self.trans.receiveBegin(): #Initialize parameters and set rx mode
            time.sleep(.05) #Maybe we could increase this value
            if self.trans.receiveDone():
                if self.trans.ACKRequested():
                    self.trans.sendACK()
                data_recv = self.trans.DATA
        return data_recv


    def write(self, data):
        if isinstance(data, SensorData.SensorData):
            #data to send: id, time, pressure, temperature, roll, pitch, yaw.
            #dimension of toSend = 61 to take advantage of the built in AES/CRC we want to limit the
            #frame size to the internal FIFO size (66 bytes - 3 bytes overhead)
            to_send = struct.pack('cdddddd', "0", data.current_data.time, data.current_data.pressure,
                                  data.current_data.temperature, data.current_data.orientation["roll"],
                                  data.current_data.orientation["pitch"],
                                  data.current_data.orientation["yaw"])
            self.trans.send(1, to_send) #When finish sending changes to rx mode
            #data to send: id, time, altitude, velocity, latitude, longitude
            to_send = struct.pack('cdddddd', "1", data.current_data.time, data.current_data.altitude,
                                  data.current_data.velocity, data.current_data.latitude,
                                  data.current_data.longitude)
            self.trans.send(1, to_send) #When finish sending changes to rx mode
        else:
            self.trans.send(1, data.__str__())

    def shutdown(self):
        self.trans.shutdown()


    def init(self):
        pass

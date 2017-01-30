from Sensors import IMU
import time
import RTIMU
from Exceptions import IMUException

"""
imu = IMU.IMU()
imu.init_sensor()
a = 0
while True:
    time.sleep(0.5)
    try:
        imu.read()
        read = imu.get_reading()
        print(read.altitude)
    except IMUException.IMUException:
        print("nope", a)
        a += 1
"""


config_file = RTIMU.Settings("RTIMULib")
imu = RTIMU.RTIMU(config_file)
pressure = RTIMU.RTPressure(config_file)
if not imu.IMUInit():
    print("IMUInit failed")
if not pressure.pressureInit():
    print("PressureInit failed")
imu.setGyroEnable(True)
imu.setAccelEnable(True)
imu.setCompassEnable(True)
imu.setSlerpPower(0.02)

while True:
    time.sleep(0.05)
    print(imu.IMURead())
    print(imu.getIMUData())

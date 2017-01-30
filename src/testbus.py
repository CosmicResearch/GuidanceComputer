import time
from Sensors import SensorBus, GPSSensor, IMUSensor

def read(data):
    print(data.__repr__())

def error(e):
    print(e)

sensorbus = SensorBus.SensorBus("./config.ini")
sensorbus.set_error_callback(error)
sensorbus.set_read_callback(read)
sensorbus.register_sensor(GPSSensor.GPSSensor())
sensorbus.register_sensor(IMUSensor.IMUSensor())
sensorbus.start_reading()
time.sleep(5)
sensorbus.stop_reading()

import time
from Sensors import GPSSensor

gpssensor = GPSSensor.GPSSensor()
gpssensor.init_sensor()
while True:
    before = time.time()
    gpssensor.read()
    print(gpssensor.current_data.latitude, gpssensor.current_data.longitude)
    print("lat, lon", gpssensor.lat, gpssensor.lon)
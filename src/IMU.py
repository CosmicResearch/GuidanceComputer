from multiprocessing import Process, Queue
import time

class IMUProcess(Process):

    def __init__(self, queue):
        Process.__init__(self)
        self.name = "IMUProcess"
        self.daemon = True
        self.queue = queue
        self.poll_rate = 10/1000 #In seconds
        self._t0 = time.time()

    def run(self):
        self._t0 = time.time()
        while True:
            data = self.read_sensors()
            self.queue.put(data)
            time.sleep(self.poll_rate)

    def read_sensors(self):
        return (time.time() - self._t0, 100, (0,0,1)) #time, altitude, orientation
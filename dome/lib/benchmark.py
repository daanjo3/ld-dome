import csv
import time

from config import BM_LOG
from multiprocessing import Process

class BenchMark(Process):

    def __init__(self, dome, lt):
        Process.__init__(self)
        self.launch_time = lt
        self.bm_queue = dome.bm_queue
        f = open(BM_LOG, 'w')
        f.close()
    
    def run(self):
        try:
            while(True):
                # Put in the name, state (start/stop) and current time
                name, ss, ts = self.bm_queue.get(block=True)
                self.write_results(name, ss, self.relative_time(ts))
        except KeyboardInterrupt:
            return
    
    def write_results(self, name, ss, ts):
        print('--- Writing to CSV file ---')
        print(name, ss, ts)
        with open(BM_LOG, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([name, ss, ts])

    def relative_time(self, t):
        rt = t - self.launch_time
        return rt
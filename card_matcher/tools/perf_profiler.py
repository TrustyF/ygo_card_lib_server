import time


class PerfProfiler:
    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.end_time = time.time()
        diff = self.end_time - self.start_time
        print(f'executed in {diff}')

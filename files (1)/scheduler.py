import threading
import time

class Scheduler:
    def __init__(self):
        self.jobs = {}

    def schedule(self, name, func, interval_sec):
        if name in self.jobs:
            self.cancel(name)
        def job_wrapper():
            while True:
                func()
                time.sleep(interval_sec)
        t = threading.Thread(target=job_wrapper)
        t.daemon = True
        t.start()
        self.jobs[name] = t

    def cancel(self, name):
        # For demo: cannot truly kill thread, just mark removed
        if name in self.jobs:
            del self.jobs[name]
import time


class Timer:
    timeStamp = 0

    def Timer(self):
        Time = max(0, self.timeStamp - time.time())
        if 0 == Time:
            return 1
        return 0

    def SetTimer(self, t):
        self.timeStamp = time.time() + t

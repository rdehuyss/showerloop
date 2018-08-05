import time


class StubUTime:

    def ticks_ms(self):
        return int(round(time.time() * 1000))
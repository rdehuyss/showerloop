from unittest import TestCase
from threading import Timer
import time


class StubTimer:
    timers = []

    def __init__(self, times_faster=10):
        self.t = None
        self.callback = None
        self.times_faster = times_faster
        print('Created stubtimer')

    def init(self, period, mode, callback):
        self.callback = callback
        sleep_time = period / (self.times_faster * 1000)
        self.t = Timer(sleep_time, self._callback_wrapper)
        self.t.start()
        StubTimer.timers.append(self.t)

    def _callback_wrapper(self):
        try:
            self.callback(None)
        except Exception as e:
            self.t.exception = e

    def deinit(self):
        self.t.cancel()

    @classmethod
    def wait_for_timers(cls):
        for timer in cls.timers:
            timer.join()
            if hasattr(timer, 'exception'):
                raise timer.exception

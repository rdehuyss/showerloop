import machine
import math
from .relay import Relay


class Valve:
    Counter = 0

    def __init__(self, open_pin, close_pin, default_state, time_to_open=5000):
        Valve.Counter = Valve.Counter + 1
        self.open_relay = Relay(open_pin)
        self.close_relay = Relay(close_pin)
        self.timer = machine.Timer(Valve.Counter)
        self.valve_counter = Valve.Counter

        self.time_to_open = time_to_open
        self.state = default_state
        self._currentRelay = None
        self._callback = None

        print("Initialized Valve ", self.valve_counter, " on pins ", open_pin, " (open) and ", close_pin, " (close)")

    def open(self, callback = None):
        self.move(1.0, callback)

    def close(self, callback = None):
        self.move(0.0, callback)

    def move(self, new_state, callback = None):
        if self._currentRelay is not None:
            raise Exception("ERROR: can't control valve if already moving")  # is this the case? Otherwise stop all control and timers and then do magic?
        self._callback = callback

        action = ""
        if new_state > self.state:
            self._currentRelay = self.open_relay
            action = " opening "
        elif new_state < self.state:
            self._currentRelay = self.close_relay
            action = " closing "

        if self._currentRelay is not None:
            time_needed = self._calculate_time_needed(new_state)
            self._currentRelay.on()
            self.timer.init(period=time_needed, mode=machine.Timer.ONE_SHOT, callback=self.move_cb)
            print("Valve ", self.valve_counter, action, "(", self._currentRelay, "), moving from ", self.state, " to ", new_state, "(time needed = ", time_needed, ")")
            self.state = new_state

    def move_cb(self, b):
        self._currentRelay.off()
        self.timer.deinit()
        self._currentRelay = None
        print("Valve ", self.valve_counter, " moved to state", self.state)
        if self._callback:
            self._callback(self.valve_counter, self.state)
            self._callback = None

    def _calculate_time_needed(self, new_state):
        start_stop_time = self.time_to_open / 10
        time_to_open_without_start_stop_time = self.time_to_open - start_stop_time

        move_time = math.fabs((new_state - self.state) * time_to_open_without_start_stop_time)
        if new_state == 0.0 or self.state == 0.0:
            move_time += start_stop_time/2
        if new_state == 1.0 or self.state == 1.0:
            move_time += start_stop_time / 2

        move_time = math.trunc(move_time)
        return move_time;

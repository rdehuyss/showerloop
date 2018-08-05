import math
import os
import time
from unittest import TestCase
import mock

from tests.StubTimer import StubTimer
from tests.StubUTime import StubUTime


class TestValve(TestCase):

    def setUp(self):
        self.mock_machine = mock.Mock()
        self.mock_utime = StubUTime()
        self.mock_machine.Timer.return_value = StubTimer()

    def test_init(self):
        self.valve = self.create_valve(1, 2, 0.0)
        self.mock_machine.Pin.assert_any_call(1, self.mock_machine.Pin.OUT)
        self.mock_machine.Pin.assert_any_call(2, self.mock_machine.Pin.OUT)
        self.mock_machine.Timer.assert_called_with(101)

    def test_open(self):
        self.valve = self.create_valve(1, 2, 0.0)
        self.valve.open(self.open_callback)
        self.valve.open_relay.pin.value.assert_any_call(0)
        self.valve.close_relay.pin.value.assert_any_call(0)
        self.valve.open_relay.pin.value.assert_any_call(1)

        StubTimer.wait_for_timers()

    def test_close_does_nothing_when_already_closed(self):
        self.valve = self.create_valve(1, 2, 0.0)
        self.valve.close()
        self.valve.open_relay.pin.value.assert_any_call(0)
        self.valve.close_relay.pin.value.assert_any_call(0)

        self.valve.open_relay.pin.value.assert_not_called_with(1)
        self.valve.close_relay.pin.value.assert_not_called_with(1)

        StubTimer.wait_for_timers()

    def test_move_partially(self):
        self.valve = self.create_valve(1, 2, 0.0)
        self.valve.move(0.20)

        StubTimer.wait_for_timers()
        self.assertEqual(230, round(self.valve.timer.time_in_millis()))  # extra time for starting

        self.valve.move(0.30)
        StubTimer.wait_for_timers()
        self.assertEqual(90, round(self.valve.timer.time_in_millis()))  # no extra time for starting

    def test_open_close(self):
        self.valve = self.create_valve(1, 2, 0.0)
        self.valve.open()
        self.valve.close()
        # TODO: make opening and closing right after each other work

    def open_callback(self, valve_counter, state):
        self.assertEqual(valve_counter, 1)
        self.assertEqual(state, 1.0)
        self.valve.open_relay.pin.value.assert_called_with(0)

    def create_valve(self, pinOpen, pinClose, default_state, time_to_open=1000):
        with mock.patch.dict('sys.modules', machine=self.mock_machine), mock.patch.dict('sys.modules', utime=self.mock_utime):
            from main.valve import Valve
            return Valve(pinOpen, pinClose, default_state, time_to_open)

    def assert_not_called_with(self, arg):
        if ((arg,),) in self.call_args_list:
            raise Exception('Error expected not be called with', arg, '. All calls: ', self.call_args_list)

    mock.Mock.assert_not_called_with = assert_not_called_with

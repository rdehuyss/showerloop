from unittest import TestCase
import mock

from tests.StubTimer import StubTimer


class TestValve(TestCase):

    def setUp(self):
        self.mock_machine = mock.Mock()
        self.mock_machine.Timer.return_value = StubTimer()
        with mock.patch.dict('sys.modules', machine=self.mock_machine):
            from main.valve import Valve
            self.valve = Valve(1, 2, 0.0)

    def test_init(self):
        self.mock_machine.Pin.assert_any_call(1, self.mock_machine.Pin.OUT)
        self.mock_machine.Pin.assert_any_call(2, self.mock_machine.Pin.OUT)
        self.mock_machine.Timer.assert_called_with(101)

    def test_open(self):
        self.valve.open(self.open_callback)
        self.valve.open_relay.pin.value.assert_any_call(0)
        self.valve.close_relay.pin.value.assert_any_call(0)
        self.valve.open_relay.pin.value.assert_any_call(1)
        StubTimer.wait_for_timers()

    def open_callback(self, valve_counter, state):
        self.assertEqual(valve_counter, 1)
        self.assertEqual(state, 1.0)
        self.valve.open_relay.pin.value.assert_called_with(0)

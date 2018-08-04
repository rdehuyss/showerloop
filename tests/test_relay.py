from unittest import TestCase
import mock


class TestRelay(TestCase):

    def setUp(self):
        self.mock_machine = mock.Mock()
        with mock.patch.dict('sys.modules', machine=self.mock_machine):
            from main.relay import Relay
            self.relay = Relay(1)

    def test_init(self):
        self.mock_machine.Pin.assert_called_once_with(1, self.mock_machine.Pin.OUT)
        self.relay.pin.value.assert_called_once_with(0)

    def test_on(self):
        self.relay.on()
        self.relay.pin.value.assert_called_with(1)

    def test_off(self):
        self.relay.off()
        self.relay.pin.value.assert_called_with(0)

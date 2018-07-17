import machine


class Relay:

    def __init__(self, pin):
        self.pin = machine.Pin(pin, machine.Pin.OUT)

    def on(self):
        self.pin.value(0)

    def off(self):
        self.pin.value(1)

    def __str__(self):
        return "pin " + str(self.pin) + " = " + str(self.pin.value())
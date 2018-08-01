import machine


class Relay:

    def __init__(self, pin):
        self.pin = machine.Pin(pin, machine.Pin.OUT)
        self.simulating_showerloop = False
        self.off()

    def on(self):
        if self.simulating_showerloop:
            print('\t', str(self))
        else:
            self.pin.value(1)

    def off(self):
        if self.simulating_showerloop:
            print('\t', str(self))
        else:
            self.pin.value(0)

    def __str__(self):
        return "pin " + str(self.pin) + " = " + str(self.pin.value())

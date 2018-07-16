import machine
import micropython


class WaterLevelSensor:

    def __init__(self, pin):
        self.state = False
        self.pin = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.pin.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=self.water_level_callback)
        self.callbacksHigh = []
        self.callbacksLow = []

        print("Initialized WaterLevelSensor on ", self.pin)

    def add_high_callback(self, func):
        if func is not None:
            self.callbacksHigh.append(func)

    def add_low_callback(self, func):
        if func is not None:
            self.callbacksLow.append(func)

    def water_level_callback(self, pin):
        if self.state != bool(pin.value()):
            self.state = bool(pin.value())
            print("Water level sensor ", pin, pin.value())
            if self.state:
                for func in self.callbacksHigh:
                    micropython.schedule(func, 0)
            else:
                for func in self.callbacksLow:
                    micropython.schedule(func, 0)


import machine
import utime
import micropython
from .ntc_temperature_sensor import NtcTemperatureSensor


class WaterFlowSensor:
    Counter = 10

    def __init__(self, pin, callback=None, ntc_temperature_sensor: NtcTemperatureSensor=None, calibration_factor=4.5):
        WaterFlowSensor.Counter = WaterFlowSensor.Counter + 1

        self.pulse_count = 0
        self.old_time = utime.ticks_ms()
        self.calibration_factor = calibration_factor
        self.flow_info = FlowInfo.stopped()

        self.timer = machine.Timer(WaterFlowSensor.Counter)
        self.timer_started = False
        self.pin = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=self.flow_callback)

        # why comment: one cannot instantiate in ISR => instantiate it in constructor
        self.calculate_flow_rate_ref = self.calculate_flow_rate

        self.flow_sensor_callback = callback
        self.ntc_temperature_sensor = ntc_temperature_sensor

        print("Initialized FlowSensor", (WaterFlowSensor.Counter - 10))

    def timer_callback(self, b):
        micropython.schedule(self.calculate_flow_rate_ref, 0)

    def flow_callback(self, pin):
        self.pulse_count = self.pulse_count + 1
        if not self.timer_started:
            self.timer_started = True
            self.timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=self.timer_callback)

    def calculate_flow_rate(self, notused):
        temperature = self._get_temperature()
        flow_rate = ((1000.0 / (utime.ticks_ms() - self.old_time)) * self.pulse_count) / self.calibration_factor;
        millilitres = (flow_rate / 60) * 1000
        pulses = self.pulse_count
        self.old_time = utime.ticks_ms()

        if flow_rate > 1:
            flow_status = FlowStatus.STARTED if self.flow_info.flowing == FlowStatus.STOPPED else FlowStatus.RUNNING
            self.flow_info = FlowInfo(flow_status, flow_rate, millilitres, pulses, temperature)
            if self.flow_sensor_callback:
                self.flow_sensor_callback(self.flow_info)
        else:
            if self.flow_info.flowing == FlowStatus.RUNNING:
                self.flow_info = FlowInfo(FlowStatus.STOPPED, flow_rate, millilitres, pulses, temperature)
                if self.flow_sensor_callback:
                    self.flow_sensor_callback(self.flow_info)
            else:
                self.flow_info = FlowInfo.stopped()
                self.timer.deinit()
                self.timer_started = False
        self.pulse_count = 0

    def _get_temperature(self):
        if self.ntc_temperature_sensor:
            return self.ntc_temperature_sensor.read_temperature()
        else:
            return -1.0


class FlowInfo:

    def __init__(self, flowing, flow_rate_per_min, millilitres, pulses, temperature):
        self.flowing = flowing
        self.flow_rate_per_min = flow_rate_per_min
        self.millilitres = millilitres
        self.pulses = pulses
        self.temperature = temperature

    def is_flowing(self):
        return self.flowing == FlowStatus.STARTED or self.flowing == FlowStatus.RUNNING

    def __str__(self):
        return str(self.flowing) + "; " \
               + str(self.flow_rate_per_min) + "L/min; " \
               + str(self.millilitres) + "ml; " \
               + str(self.pulses) + "pulses; " \
               + str(self.temperature) + "C"

    @staticmethod
    def stopped():
        return FlowInfo(FlowStatus.STOPPED, 0.0, 0, 0, -1)

class FlowStatus:
    STARTED = 1
    RUNNING = 2
    STOPPED = 3

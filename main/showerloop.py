import utime
import os
import machine
import micropython
import builtins

from .water_level_sensor import WaterLevelSensor
from .water_level_controller import WaterLevelController
from .water_flow_sensor import WaterFlowSensor, FlowInfo
from .ntc_temperature_sensor import NtcTemperatureSensor
from .valve import Valve
from .relay import Relay
from .mqttclient import MQTTPublisher
from ota_update.main.ota_updater import OTAUpdater


class ShowerLoop:

    def __init__(self, config_data):
        self.showerloopState = ShowerLoopStatus()

        cold_water_temperature_sensor = NtcTemperatureSensor(config_data["coldWaterFlowSensor"]["temperatureSensorPin"])
        self.coldWaterFlowSensor = WaterFlowSensor(config_data["coldWaterFlowSensor"]["flowPin"], cold_water_temperature_sensor)
        hot_water_temperature_sensor = NtcTemperatureSensor(config_data["hotWaterFlowSensor"]["temperatureSensorPin"])
        self.hotWaterFlowSensor = WaterFlowSensor(config_data["hotWaterFlowSensor"]["flowPin"], hot_water_temperature_sensor)
        self.waterLevelLowSensor = WaterLevelSensor(config_data["waterLevelSensor"]["lowPin"])
        self.waterLevelLowSensor.add_high_callback(self.low_water_level_reached_callback)
        self.waterLevelHighSensor = WaterLevelSensor(config_data["waterLevelSensor"]["highPin"])
        self.drainValve = Valve(config_data["drainValve"]["openPin"], config_data["drainValve"]["closePin"], 1.0, 14500)
        self.coldWaterSupplyValve = Valve(config_data["coldWaterSupplyValve"]["openPin"], config_data["coldWaterSupplyValve"]["closePin"], 1.0)
        self.recuperationWaterSupplyValve = Valve(config_data["recuperationWaterSupplyValve"]["openPin"], config_data["recuperationWaterSupplyValve"]["closePin"], 0.0)
        self.waterLevelController = WaterLevelController(self.drainValve, self.waterLevelLowSensor, self.waterLevelHighSensor)
        self.waterPumpRelay = Relay(config_data["waterPump"]["pin"])
        self.uvcLampRelay = Relay(config_data["uvcLamp"]["pin"])

        self.hot_water_flow_rate = FlowInfo.stopped()
        self.cold_water_flow_rate = FlowInfo.stopped()

        self.showerloopStats = ShowerLoopStats()
        self.mqttPublisher = MQTTPublisher(config_data)

        self.valves_ready_counter = 0

        self.waterFlowSensorTimer = machine.Timer(0)
        self.waterFlowSensorTimer.init(period=1000, mode=machine.Timer.PERIODIC, callback=self.water_flow_sensor_timer_callback)
        # why comment: one cannot instantiate in ISR => instantiate it in constructor
        self.check_water_flow_sensors_ref = self.check_water_flow_sensors

        # why comment: for testing purposes
        self.simulate_only = False
        self.stub_water_flowing = False

        print('Showerloop ', self.get_version('main'), 'up & running')

    def low_water_level_reached_callback(self, not_important):
        self.start_pumping()

    def start_fsm(self):
        if self.is_water_flowing():
            if self.showerloopState.is_initial():
                if self.hot_water_flow_rate.temperature > 20:
                    self.start_showerloop()
                else:
                    print("Waiting for water temp", self.hot_water_flow_rate.temperature)
        else:
            if self.showerloopState.is_started():
                self.stop_showerloop()

        if self.showerloopState.is_started():
            self.showerloopStats.add_hot_water_flow(self.hot_water_flow_rate)
            self.showerloopStats.add_recuperation_water_flow(self.cold_water_flow_rate)
        else:
            self.showerloopStats.add_hot_water_flow(self.hot_water_flow_rate)
            self.showerloopStats.add_cold_water_flow(self.cold_water_flow_rate)

        self.mqttPublisher.publish(self.showerloopStats)

    def start_showerloop(self):
        self.mqttPublisher.connect()
        self.showerloopStats.start()
        self.showerloopState.starting()
        self.drainValve.close()

    def start_pumping(self):
        if self.showerloopState.is_starting():
            self.waterPumpRelay.on()
            self.uvcLampRelay.on()
            utime.sleep_ms(300)
            self.recuperationWaterSupplyValve.open()
            utime.sleep_ms(300)
            self.coldWaterSupplyValve.close()
            self.waterLevelController.start_controlling()
            self.showerloopState.started()

    def stop_showerloop(self):
        if self.showerloopState.is_started():
            self.waterPumpRelay.off()
            self.uvcLampRelay.off()
            self.waterLevelController.stop_controlling()
            self.drainValve.open(self.reset_on_all_valves_close)
            self.coldWaterSupplyValve.open(self.reset_on_all_valves_close)
            self.recuperationWaterSupplyValve.close(self.reset_on_all_valves_close)

            self.showerloopState.stopped()
            self.mqttPublisher.disconnect()

    def reset_on_all_valves_close(self, valve, state):
        self.valves_ready_counter += 1
        if self.valves_ready_counter >= 3:
            if self.mqttPublisher.connected:
                # After each shower check for updates as we already have a WIFI connection
                o = OTAUpdater('https://github.com/rdehuyss/showerloop')
                o.check_for_update_to_install_during_next_reboot()

            # Start over for next shower and disable wifi
            machine.reset()

    def is_water_flowing(self):
        return self.cold_water_flow_rate.is_flowing() or self.hot_water_flow_rate.is_flowing() or self.stub_water_flowing

    def water_flow_sensor_timer_callback(self, notused):
        micropython.schedule(self.check_water_flow_sensors_ref, 0)

    def check_water_flow_sensors(self, notused):
        self.cold_water_flow_rate = self.coldWaterFlowSensor.calculate_flow_rate()
        self.hot_water_flow_rate = self.hotWaterFlowSensor.calculate_flow_rate()

        if self.is_water_flowing() or not self.showerloopState.is_initial():
            self.start_fsm()

    def enable_simulation(self):
        builtins.simulating_showerloop = True

    def get_version(self, directory):
        if '.version' in os.listdir(directory):
            f = open(directory + '/.version')
            version = f.read()
            f.close()
            return version
        return '0.0'


class ShowerLoopStatus:
    _INITIAL = 0
    _STARTING = 1
    _STARTED = 2
    _STOPPED = 3

    state = 0

    def starting(self):
        self.state = ShowerLoopStatus._STARTING
        print("ShowerLoop is Starting")

    def started(self):
        self.state = ShowerLoopStatus._STARTED
        print("ShowerLoop is Started")

    def stopped(self):
        self.state = ShowerLoopStatus._STOPPED
        print("ShowerLoop is Stopped")

    def is_initial(self):
        return self.state == ShowerLoopStatus._INITIAL

    def is_started(self):
        return self.state == ShowerLoopStatus._STARTED

    def is_starting(self):
        return self.state == ShowerLoopStatus._STARTING

    def is_stopped(self):
        return self.state == ShowerLoopStatus._STOPPED

    def __str__(self):
        if self.is_initial():
            return "INITIAL"
        elif self.is_starting():
            return "STARTING"
        elif self.is_started():
            return "STARTED"
        elif self.is_stopped():
            return "STOPPED"
        else:
            raise Exception("Illegal state: ", self.state)


class ShowerLoopStats:

    def __init__(self):
        self.start_time = -1
        self.stop_time = -1
        self.running = False

        self.hot_water_pulses = 0
        self.hot_water_total_millilitres = 0
        self.hot_water_avg_temp = 0

        self.cold_water_pulses = 0
        self.cold_water_total_millilitres = 0
        self.cold_water_avg_temp = 0

        self.recuperation_water_pulses = 0
        self.recuperation_water_total_millilitres = 0
        self.recuperation_water_avg_temp = 0

    def start(self):
        self.start_time = utime.ticks_ms()
        self.running = True

    def stop(self):
        self.stop_time = utime.ticks_ms()
        self.running = False

    def add_hot_water_flow(self, flow_rate: FlowInfo):
        self.hot_water_pulses += flow_rate.pulses
        self.hot_water_total_millilitres += flow_rate.millilitres
        self.hot_water_avg_temp = self._calculate_temp(self.hot_water_avg_temp, flow_rate.temperature)
        self.stop_time = utime.ticks_ms()  # we update the stop time so we can send it via mqtt

    def add_cold_water_flow(self, flow_rate: FlowInfo):
        self.cold_water_pulses += flow_rate.pulses
        self.cold_water_total_millilitres += flow_rate.millilitres
        self.cold_water_avg_temp = self._calculate_temp(self.cold_water_avg_temp, flow_rate.temperature)

    def add_recuperation_water_flow(self, flow_rate: FlowInfo):
        self.recuperation_water_pulses += flow_rate.pulses
        self.recuperation_water_total_millilitres += flow_rate.millilitres
        self.recuperation_water_avg_temp = self._calculate_temp(self.recuperation_water_avg_temp, flow_rate.temperature)

    def __str__(self):
        return "\n\tHot water: " + str(self._calculate_L_per_min(self.hot_water_total_millilitres)) + " L/min; " + str(self.hot_water_total_millilitres) + " ml; " + str(self.hot_water_pulses) + " pulses; " + str(
            self.hot_water_avg_temp) + " C" \
                                       "\n\tCold water: " + str(self._calculate_L_per_min(self.cold_water_total_millilitres)) + " L/min; " + str(self.cold_water_total_millilitres) + " ml; " + str(self.cold_water_pulses) + " pulses; " + str(
            self.cold_water_avg_temp) + " C" \
                                        "\n\tRecuperation water: " + str(self._calculate_L_per_min(self.recuperation_water_total_millilitres)) + " L/min; " + str(self.recuperation_water_total_millilitres) + " ml; " + str(
            self.recuperation_water_pulses) + " pulses; " + str(self.recuperation_water_avg_temp) + " C"

    def _calculate_L_per_min(self, millilitres):
        return (millilitres / 1000) / ((self.stop_time - self.start_time) / (1000 * 60))

    @staticmethod
    def _calculate_temp(avg, new_temp):
        if avg < 1:
            return new_temp
        elif new_temp < 1:
            return avg
        else:
            return (avg + new_temp) / 2

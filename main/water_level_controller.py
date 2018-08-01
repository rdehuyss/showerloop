from .valve import Valve
from .water_level_sensor import WaterLevelSensor


class WaterLevelController:

    def __init__(self, valve: Valve, low_water_level_sensor: WaterLevelSensor, high_water_level_sensor: WaterLevelSensor):
        self.is_controlling = False
        self.valve = valve
        self.low_water_level_sensor = low_water_level_sensor
        self.low_water_level_sensor.add_low_callback(self.low_water_level_sensor_low_callback)
        self.high_water_level_sensor = high_water_level_sensor
        self.high_water_level_sensor.add_low_callback(self.high_water_level_sensor_low_callback)
        self.high_water_level_sensor.add_high_callback(self.high_water_level_sensor_high_callback)

        print("Initialized WaterLevelController")

    def start_controlling(self):
        self.is_controlling = True

    def low_water_level_sensor_low_callback(self, pin):
        if self.is_controlling:
            self.valve.close()

    def high_water_level_sensor_low_callback(self, pin):
        if self.is_controlling:
            self.valve.move(0.15)

    def high_water_level_sensor_high_callback(self, pin):
        if self.is_controlling:
            self.valve.move(0.25)

    def stop_controlling(self):
        self.is_controlling = False
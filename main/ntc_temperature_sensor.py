import machine
import utime
import math


class NtcTemperatureSensor:

    def __init__(self, pin, thermistornominal=50000, temperaturenominal=25, bcoefficient=3950, seriesresistor=47000):
        self.calc = NtcCalculator(thermistornominal, temperaturenominal, bcoefficient, seriesresistor)
        self.adc = machine.ADC(machine.Pin(pin))
        self.adc.atten(self.adc.ATTN_11DB)

    def read_temperature(self):
        adc_total = 0
        for i in range(5):
            adc_value = self.adc.read()
            adc_total += adc_value
            utime.sleep_ms(20)
        return self.calc.calculate_temperature(adc_total/5)


class NtcCalculator:

    def __init__(self, thermistor_nominal=50000, temperature_nominal=25, b_coefficient=3950, series_resistor=47000):
        self.thermistor_nominal = thermistor_nominal
        self.temperature_nominal = temperature_nominal
        self.b_coefficient = b_coefficient
        self.series_resistor = series_resistor

    def calculate_temperature(self, adc_value):
        resistance = self.calculate_resistance(adc_value)
        steinhart = resistance / self.thermistor_nominal
        steinhart = math.log(steinhart)
        steinhart /= self.b_coefficient
        steinhart += 1.0 / (self.temperature_nominal + 273.15)
        steinhart = 1.0 / steinhart
        steinhart -= 273.15
        return steinhart

    def calculate_resistance(self, adc_value):
        voltage = self.calculate_voltage(adc_value)
        return (voltage * self.series_resistor) / (3.3 - voltage)

    @staticmethod
    def calculate_voltage(adc_value):
        return -0.000000000000016 * pow(adc_value, 4) + 0.000000000118171 * pow(adc_value, 3) - 0.000000301211691 * \
               pow(adc_value, 2) + 0.001109019271794 * adc_value + 0.034143524634089;

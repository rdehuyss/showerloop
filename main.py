import utime
import script



def main():

    valve = Valve(5, 6)
    while True:
        print('Opening')
        valve.open()
        utime.sleep_ms(5000)
        print('Closing')
        valve.close()
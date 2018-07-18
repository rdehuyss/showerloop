import ujson
import utime
from ntptime import NTPProvider
from ota_update.main.ota_updater import OTAUpdater


def apply_updates_if_available():
    o = OTAUpdater('https://github.com/rdehuyss/showerloop')
    o.apply_pending_updates_if_available()


def start(config_data):
    utime.sleep_ms(10000)
    from main.showerloop import ShowerLoop
    ShowerLoop(config_data)


def test():
    NTPProvider.set_machine_time()

    f = open('config.json')
    config_data = ujson.load(f)

    apply_updates_if_available()
    start(config_data)


import ujson
import utime
from ota_update.main.ota_updater import OTAUpdater


def apply_updates_if_available(config_data):
    o = OTAUpdater('https://github.com/rdehuyss/showerloop')
    o.apply_pending_updates_if_available()


def start(config_data):
    utime.sleep_ms(30000)
    from main.showerloop import ShowerLoop
    ShowerLoop(config_data)


def main():
    f = open('config.json')
    config_data = ujson.load(f)

    apply_updates_if_available(config_data)
    start(config_data)

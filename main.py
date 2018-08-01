import ujson
import utime
from ota_update.main.ota_updater import OTAUpdater


def download_and_install_update_if_available(config_data):
    if 'wifi' in config_data:
        o = OTAUpdater('https://github.com/rdehuyss/showerloop')
        o.download_and_install_update_if_available(config_data['wifi']['ssid'], config_data['wifi']['password'])
    else:
        print('No WIFI configured, skipping updates check')


def start(config_data):
    global s
    utime.sleep_ms(10000)
    from main.showerloop import ShowerLoop
    s = ShowerLoop(config_data)


def boot_showerloop():
    f = open('config.json')
    config_data = ujson.load(f)

    download_and_install_update_if_available(config_data)
    start(config_data)


s = None
boot_showerloop()

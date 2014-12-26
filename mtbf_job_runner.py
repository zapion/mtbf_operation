#!/usr/bin/env python

import os
from combo_runner import action_decorator
from combo_runner.base_action_runner import BaseActionRunner
from marionette import Marionette
import mozdevice
from gaiatest import GaiaData, GaiaApps, GaiaDevice
from utils import zip_utils
from utils.device_pool import DevicePool

action = action_decorator.action


class MtbfJobRunner(BaseActionRunner):
    
    BRANCH_V210_KK = 'mozilla-b2g34_v2_1-flame-kk-eng'
    GECKO_B2G34 = 'b2g-34.0.en-US.android-arm.tar.gz'
    SYMBOLS_B2G34 = 'b2g-34.0.en-US.android-arm.crashreporter-symbols.zip'

    def __init__(self, deviceSerial=None, **kwargs):
        deviceSerial and self.setup(deviceSerial)
        BaseActionRunner.__init__(self)

    def setup(self, deviceSerial):
        if not hasattr(self, 'marionette') or not self.marionette:
            os.environ['BRANCH'] = self.BRANCH_V210_KK
            os.environ['GECKO'] = self.GECKO_B2G34
            os.environ['SYMBOLS'] = self.SYMBOLS_B2G34
            os.environ['GAIA'] = 'gaia.zip'
            self.deviceSerial = deviceSerial
            self.dm = mozdevice.DeviceManagerADB(deviceSerial)
            self.marionette = Marionette()
            self.marionette.start_session()
            self.apps = GaiaApps(self.marionette)
            self.data_layer = GaiaData(self.marionette)
            self.device = GaiaDevice(self.marionette)

    @action
    def download_pvt_b2g(self, action=False):
        ## TODO: finish download process
        ## Adapting python version flash tool
        self.pre_commands.append('./mtbf_download_pvt_b2g.sh')
        return self

    @action
    def add_7mobile_action(self, action=True):
        self.data_layer.set_setting('ril.data.apnSettings',
                                    [[
                                        {"carrier": "(7-Mobile) (MMS)",
                                            "apn": "opentalk",
                                            "mmsc": "http://mms",
                                            "mmsproxy": "210.241.199.199",
                                            "mmsport": "9201",
                                            "types": ["mms"]},
                                        {"carrier": "(7-Mobile) (Internet)",
                                            "apn": "opentalk",
                                            "types": ["default", "supl"]}
                                    ]])
        return

    @action
    def change_memory(self, memory=0, action=False):
        # make sure it's in fastboot mode, TODO: leverage all fastboot command in one task function
        mem_str = str(memory)
        if memory == 0:
            mem_str = "auto"
        os.system("fastboot setvar mem " + mem_str)
        #TODO: use adb/fastboot command to change memory?

    @action
    def collect_memory_report(self, action=True):
        zip_utils.collect_about_memory("mtbf_driver")  # TODO: give a correct path for about memory folder

    def get_free_device(self, action=True):
        dp = DevicePool()
        if dp and dp.get_lock():
            # Record device serial and store dp instance
            self.serial = str(dp)
            self.dp = dp
            os.environ["ANDROID_SERIAL"] = self.serial
            self.setup(self.serial)
            port = self.find_available_port()
            if self.port_forwarding(str(dp), port):
                return dp
            print "Port forwarding failed"
            return None
        print "No available device.  Please retry after device released"
        # TODO: more handling for no available device

    @action
    def full_flash(self, action=False, device='flame-kk', branch='mozilla-central', build_type='Engineer', build_id=''):
        pass

    @action
    def shallow_flash(self, action=True, device='flame-kk', branch='mozilla-central', build_type='Engineer', build_id=''):
        pass

    def port_forwarding(self, serial, port):
        if serial and port:
            os.system("adb -s " + serial + " forward tcp:" + port + " tcp:2828")

    def find_avaiable_port(self):
        if 'ANDROID_SERIAL' in os.environ.keys():
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('', 0))
            port = sock.getsockname()[1]
            sock.close()
            return port

    @action
    def enable_certified_apps_debug(self, action=True):
        if self.serial:
            os.system("B2G-flash-tool/enable_certified_apps_for_devtools.sh")
            return True
        return False

    def release(self):
        if hasattr(self, 'dp') and self.dp:
            self.dp.release()
            return True
        else:
            print "No device allocated"
            return False

    def execute(self):
        # run test runner here
        pass

    def pre_flash(self):
        pass

    def flash(self):
        self.shallow_flash()
        self.full_flash()

    def post_flash(self):
        self.add_7mobile_action()
        #self.enable_certified_apps_debug()

    def run(self):
        try:
            if self.get_free_device():
                self.pre_flash()
                self.flash()
                self.post_flash()
                self.execute()
        finally:
            self.release()

if __name__ == '__main__':
    mjr = MtbfJobRunner()
    mjr.run()

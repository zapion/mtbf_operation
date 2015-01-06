#!/usr/bin/env python

import os
import subprocess
from combo_runner import action_decorator
from combo_runner.base_action_runner import BaseActionRunner
from marionette import Marionette
import mozdevice
from gaiatest import GaiaData, GaiaApps, GaiaDevice
from utils import zip_utils
from utils.device_pool import DevicePool


action = action_decorator.action



class MtbfJobRunner(BaseActionRunner):
    flash_params = {
            'device': '',
            'branch': 'mozilla-b2g34_v2_1-flame-kk-eng',
            'build': '',
            'build_id': ''
            }
    BRANCH_V210_KK = 'mozilla-b2g34_v2_1-flame-kk-eng'
    GECKO_B2G34 = 'b2g-34.0.en-US.android-arm.tar.gz'
    SYMBOLS_B2G34 = 'b2g-34.0.en-US.android-arm.crashreporter-symbols.zip'

    def __init__(self, deviceSerial=None, **kwargs):
        deviceSerial and self.setup(deviceSerial)
        BaseActionRunner.__init__(self)

    def setup(self, deviceSerial):
        # TODO: Adding setting flash params function
        
        if not hasattr(self, 'marionette') or not self.marionette:
            self.deviceSerial = deviceSerial
            self.dm = mozdevice.DeviceManagerADB(deviceSerial)
            self.marionette = Marionette()
            self.marionette.start_session()
            self.apps = GaiaApps(self.marionette)
            self.data_layer = GaiaData(self.marionette)
            self.device = GaiaDevice(self.marionette)

    def adb_test(self):
        if not hasattr(self, 'serial') or os.system("adb -s " + self.serial + " shell ls") != 0:
            print("Device not found or can't be controlled")
            return False
        return True

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
        #TODO: use native adb/fastboot command to change memory?
        # Make sure it's in fastboot mode, TODO: leverage all fastboot command in one task function
        if self.adb_test():
            os.system("adb reboot boot-loader")
        mem_str = str(memory)
        os.system("fastboot setvar mem " + mem_str)
        # Preventing from async timing of fastboot
        time.sleep(5)
        os.system("fastboot reboot")

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
            port = self.find_available_port()
            if self.port_forwarding(str(dp), port):
                self.setup(self.serial)
                return dp
            print "Port forwarding failed"
            return None
        print "No available device.  Please retry after device released"
        # TODO: more handling for no available device

    @action
    def full_flash(self, action=False, flash_args=[]):
        if not flash_args:
            pass
        pass

    @action
    def shallow_flash(self, action=True, flash_args=[]):
        if not flash_args:
            pass

    def port_forwarding(self, serial, port):
        out = subprocess.check_output(['/usr/bin/adb version'], shell=True)
        import re
        search = re.search('[0-9\.]+', out)
        if search and search.group(0) >= '1.0.31':
            out = subprocess.check_output('/usr/bin/adb forward --list', shell=True)
            if re.search('\w+', out).group(0) == serial:
                # Use existing forwarded connection
                re.search(' tcp:(\d+) ', out).group(1)
                return True
        if serial and port:
            os.system("adb -s " + serial + " forward tcp:" + str(port) + " tcp:2828")

    def find_available_port(self):
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
    def check_version(self):
        # TODO: fix check version to use package import
        os.system("cd flash_tool/ && NO_COLOR=TRUE ./check_versions.py && cd ..")

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
        self.enable_certified_apps_debug()

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
    #mjr.check_version()
    mjr.run()

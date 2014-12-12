#!/usr/bin/env python

from combo_runner import action_decorator
from combo_runner.base_action_runner import BaseActionRunner
from marionette import Marionette
import mozdevice
from gaiatest import GaiaData, GaiaApps, GaiaDevice
from utils import zip_utils
from utils.device_pool import DevicePool

action = action_decorator.action

class MtbfJobRunner(BaseActionRunner):    
    
    def __init__(self, deviceSerial=None, **kwargs):
        deviceSerial and self.setup(deviceSerial)
        BaseActionRunner.__init__(self)

    def setup(self, deviceSerial):
        if not self.marionette:
            self.dm = mozdevice.DeviceADB(deviceSerial, **kwargs)
            self.marionette = Marionette()
            self.marionette.start_session()
            self.apps = GaiaApps(self.marionette)
            self.data_layer = GaiaData(self.marionette)
            self.device = GaiaDevice(self.marionette)

    def pre_flash(self):
        pass

    def flash(self):
        pass

    def post_flash(self):
        pass

    @action
    def add_7mobile_action(self, action=False):
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
        #TODO: use adb/fastboot command to change memory?

    @action
    def collect_memory_report(self, action=True):
        zip_utils.collect_about_memory("mtbf_driver") # TODO: give a correct path for about memory folder

    @action
    def get_free_device(self, action=True):
        dp = DevicePool()
        if dp.get_lock():
            # Record device serial and store dp instance
            self.serial = str(dp)
            self.dp = dp


if __name__ == '__main__':
    mjr = MtbfJobRunner()
    mjr.get_free_device()
    mjr.dp.release()

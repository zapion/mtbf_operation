#!/usr/bin/env python
from lockfile import LockFile, NotLocked
import os
import logging
import subprocess


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DevicePool(object):
    lock_folder = "/tmp/LOCKS"
    my_lock = None
    serial = None
    current_lock_index = -1

    def __init__(self, deviceSerial=None):
        self.devices = self._device_list()
        if deviceSerial:
            self.serial = deviceSerial
            self._check_serial_in_devices()
        if not os.path.exists(self.lock_folder):
            os.makedirs(self.lock_folder)
        self.lock_list = self._get_lock_list()

    def _check_serial_in_devices(self):
        if self.serial:
            chk_list = filter(lambda x: x == self.serial, self.devices)
            if not chk_list:
                logger.warning("Android serial[" + self.serial + "] can't be found")
                return False
            else:
                return True

    def _device_list(self):
        # adb devices here
        device_list = subprocess.check_output(['adb', 'devices']).splitlines()
        device_list.pop(0)  # remove the description from adb
        device_list = map(lambda x: x.split("\t")[0], filter(lambda x: x, device_list))
        return device_list

    def _lock_list(self):
        return map(lambda x: x.split(".")[0],
                   filter(lambda x: 'lock' in x,
                          subprocess.check_output(['ls', self.lock_folder]).splitlines()))

    def _get_lock_list(self):
        lock_list = []
        for device in self.devices:
            lock_path = os.path.join(self.lock_folder, device)
            lock_list.append(LockFile(lock_path))
        return lock_list

    def __str__(self):
        if self.my_lock:
            return os.path.basename(self.my_lock.path).split('.')[0]
        return ''

    def get_lock(self):
        if self.my_lock:
            return self.my_lock
        # TODO: acquire another lock to ensure critical section (?) test if it is necessary
        for index in range(len(self.lock_list)):
            try:
                if not self.lock_list[index].i_am_locking():
                    self.lock_list[index].acquire(timeout=60)
                    # successfully get lock, return lock.path
                    self.my_lock = self.lock_list[index]
                    self.current_lock_index = index
                    return self.lock_list[index].path
            except:
                # fail to get lock eventually, TODO: raise corresponding exception
                logger.error("Failed to get lock!!")
                pass
        return None

    def get_next_lock(self):
        for next_index in range(self.current_lock_index + 1, len(self.lock_list)):
            try:
                if not self.lock_list[next_index].i_am_locking():
                    self.lock_list[next_index].acquire(timeout=60)
                    self.my_lock = self.lock_list[next_index]
                    self.current_lock_index = next_index
                    return self.lock_list[next_index].path
            except:
                logger.error("Failed to get lock!!")
                pass
        return None

    def release(self):
        if not self.my_lock:
            logger.info("No lock acquired")
            return
        try:
            self.my_lock.release()
        except NotLocked:
            logger.info("Lock is released")
        self.my_lock = None


if __name__ == '__main__':
    dp = DevicePool()
    dp._device_list()
    dp.get_lock()
    dp._lock_list()
    dp.release()

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

    def __init__(self, deviceSerial=None):
        if deviceSerial:
            self.serial = deviceSerial
        if not os.path.exists(self.lock_folder):
            os.makedirs(self.lock_folder)

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

    def __str__(self):
        if self.my_lock:
            return os.path.basename(self.my_lock.path).split('.')[0]
        return ''

    def get_lock(self):
        if self.my_lock:
            return self.my_lock
        # TODO: acquire another lock to ensure critical section (?) test if it is necessary
        devices = self._device_list()
        if self.serial:
            filter(lambda x: x == self.serial, devices)
            if not device:
                logger.warning("Android serial[" + self.serial + "] can't be found")
        lock_list = []
        for device in devices:
            lock_path = os.path.join(self.lock_folder, device)
            lock_list.append(LockFile(lock_path))

        for lock in lock_list:
            try:
                if not lock.i_am_locking():
                    lock.acquire(timeout=60)
                    # successfully get lock, return lock.path
                    self.my_lock = lock
                    return lock.path
            except:
                # fail to get lock eventually, TODO: raise corresponding exception
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


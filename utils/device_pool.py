#!/usr/bin/env python
import os
import logging
import subprocess
import re
import socket
import traceback
from random import shuffle

from mozdevice.devicemanager import DMError
from lockfile import LockFile, NotLocked

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeviceObject(object):
    lock_file_folder = "/tmp/LOCKS"

    def __init__(self, serial):
        self.serial = serial
        self.lock_file_path = None
        self.lock_file = None
        self.adb_forwarded_port = None
        self._gen_lock_file_from_serial()

    def __str__(self):
        return self.serial

    def _gen_lock_file_from_serial(self):
        if not os.path.exists(self.lock_file_folder):
            os.makedirs(self.lock_file_folder)
        self.lock_file_path = os.path.join(self.lock_file_folder, self.serial)
        self.lock_file = LockFile(self.lock_file_path)
        return self.lock_file

    def _gen_serial_from_lock(self):
        self.serial = os.path.basename(self.lock_file.path).split('.')[0]
        return self.serial

    def _find_available_port(self):
        os.environ["ANDROID_SERIAL"] = self.serial
        if 'ANDROID_SERIAL' in os.environ.keys():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('', 0))
            port = sock.getsockname()[1]
            sock.close()
            return port

    @property
    def is_file_locked(self):
        return self.lock_file.i_am_locking()

    @property
    def is_in_forwarded_list(self):
        out = exec_process(['/usr/bin/adb', 'version'])
        search = re.search('[0-9\.]+', out)
        os.system("ANDROID_SERIAL=" + self.serial + " adb wait-for-device")
        if search and search.group(0) >= '1.0.31':
            ret = subprocess.call('/usr/bin/adb forward --list |grep ' + self.serial, shell=True, stdout=open(os.devnull, 'w'))
            if ret == 0:
                return True
            else:
                return False
        else:
            logger.error("adb forward --list not supported; recommend to upgrade 1.0.31 or newer version")
            return False

    @property
    def get_adb_forwarded_port(self):
        out = exec_process(['/usr/bin/adb', 'version'])
        search = re.search('[0-9\.]+', out)
        os.system("ANDROID_SERIAL=" + self.serial + " adb wait-for-device")
        if search and search.group(0) >= '1.0.31':
            forward_list = exec_process(['/usr/bin/adb', 'forward', '--list']).splitlines()
            for out in forward_list:
                search_serial = re.search('\w+', out)
                if search_serial and search_serial.group(0) == self.serial:
                    logger.info("DeviceSerial[" + self.serial + "] forwarded")
                    return int(re.search(' tcp:(\d+) ', out).group(1))
        else:
            logger.info("adb forward --list not supported; recommend to upgrade 1.0.31 or newer version")
        return None

    def acquire_file_lock(self):
        self.lock_file.acquire(timeout=60)
        return self.lock_file.path

    def release_file_lock(self):
        try:
            self.lock_file.release()
        except NotLocked:
            logger.info("Lock is released")
        self.lock_file = None

    def create_adb_forward(self, specify_port=None):
        if self.is_in_forwarded_list:
            self.adb_forwarded_port = self.get_adb_forwarded_port
            logger.info("Using existing port [" + str(self.adb_forwarded_port) + "]")
            return True
        if specify_port:
            self.adb_forwarded_port = specify_port
        else:
            self.adb_forwarded_port = self._find_available_port()
        if self.serial and self.adb_forwarded_port:
            ret = os.system("ANDROID_SERIAL=" + self.serial + " adb forward tcp:" + str(self.adb_forwarded_port) + " tcp:2828")
            if ret != 0:
                raise DMError("can't forward port to ANDROID_SERIAL[" + self.serial + "]")
        logger.info("Port forwarding success serial:[" + self.serial + "] port:[" + str(self.adb_forwarded_port) + "]")
        return True

    def remove_adb_forward(self):
        # Remove port forwarding
        ret = os.system("ADNDROID_SERIAL=" + self.serial + " adb forward --remove tcp:" + str(self.adb_forwarded_port))
        if ret != 0:
            raise DMError("can't forward port to ANDROID_SERIAL[" + self.serial + "]")


def _gen_serial_list():
    # adb devices here
    tmp_list = exec_process(['/usr/bin/adb', 'devices']).splitlines()
    tmp_list.pop(0)  # remove the description from adb
    serial_list = map(lambda x: x.split("\t")[0], filter(lambda x: x, tmp_list))
    return serial_list


def _gen_device_obj_map():
    obj_map = {}
    shuffle(serial_list)
    for serial in serial_list:
        tmp_object = DeviceObject(serial)
        if serial in obj_map.keys():
            logging.error("Duplicate serial in serial list!!")
        else:
            obj_map[serial] = tmp_object
    return obj_map


def exec_process(cmd_list):
    # Writing this function to avoid when we call subprocess.check_output will raise OSError 24 ..
    proc = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = proc.communicate()[0]
    if proc.stdin:
        proc.stdin.close()
    if proc.stdout:
        proc.stdout.close()
    if proc.stderr:
        proc.stderr.close()
    return output


def get_device(specify_serial=None):
    global current_device_object
    if specify_serial and chk_serial_exist(specify_serial):
        current_device_object.serial = device_obj_map[specify_serial]
    if current_device_object:
        logger.info("Use current device object instead of take new obj!")
        return current_device_object
    for serial_key in device_obj_map.keys():
        try:
            if not device_obj_map[serial_key].is_file_locked and not device_obj_map[serial_key].is_in_forwarded_list:
                device_obj_map[serial_key].acquire_file_lock()
                current_device_object = device_obj_map[serial_key]
                logger.info("Get device with serial [" + serial_key + "]!")
                return device_obj_map[serial_key]
        except:
            # fail to get lock e
            # ventually, TODO: raise corresponding exception
            logger.error(traceback.format_exc())
            logger.error("Failed to get lock!!")
            pass
    logger.warning("No available device.  Please retry after device released")
    return None


def release():
    global current_device_object
    if not current_device_object:
        logger.info("No device in use!")
        return
    try:
        current_device_object.release_file_lock()
    except NotLocked:
        logger.info("File lock is released")

    if current_device_object.is_in_forwarded_list:
        # Remove port forwarding
        current_device_object.remove_adb_forward()

    current_device_object = None


def chk_serial_exist(serial):
    chk_list = filter(lambda x: x == serial, serial_list)
    if not chk_list:
        logger.warning("Android serial[" + serial + "] can't be found")
        return False
    else:
        return True

current_device_object = None
serial_list = _gen_serial_list()
device_obj_map = _gen_device_obj_map()


if __name__ == '__main__':
    do = get_device()
    if do:
        do.create_adb_forward()
    release()

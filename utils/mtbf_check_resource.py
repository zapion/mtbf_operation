## #!/usr/bin/env python
## from lockfile import LockFile
## import os
## import time
## 
## class DevicePool(object):
##     lock_folder = "/tmp/LOCKS"
##     my_lock = None
## 
##     def __init__(self):
##         pass
## 
##     def _device_list(self):
##         # adb devices here
##         pass
## 
##     def __str__(self):
##         return self.myLock
## 
##     def get_lock(self):
##         if self.my_lock:
##             return self.my_lock
##         # TODO: acquire another lock to ensure critical section (?) test if it is necessary 
##         devices = self._device_list()
##         lock_list = {}
##         for device in devices:
##             lock_path = os.path.join(lock_folder, device)
##             lock_list.append(LockFile(lock_path))
## 
##         trial = 0
##         while trial > 18:
##             for lock in lock_list:
##                 if not lock.i_am_locking:
##                     try:
##                         lock.acquire(timeout=60)
##                         # successfully get lock, return lock.path
##                         self.my_lock = lock
##                         return lock.path
##             trial += 1
##             time.sleep(10)
##         # fail to get lock eventually, TODO: raise corresponding exception
##         return None
## 
## 
## 
## 
## #!/bin/bash

# go to desired folder : /tmp
cd /tmp
TEMP_FOLDER=LOCKS
if [[ ! -d $TEMP_FOLDER ]]; then
    mkdir -p $TEMP_FOLDER
fi
cd $TEMP_FOLDER

# check and create critical section
LOCK_FILE=LOCKED
if [[ -f $LOCK_FILE ]]; then
    COUNTER=1
    while [[ $COUNTER -le 18 ]]
    do
        echo "Another thread is checking resources."
        sleep 10
        if [[ ! -f $LOCK_FILE ]]; then
            echo "Get into the critical section"
            touch $LOCK_FILE
        fi
        COUNTER=$COUNTER+1
    done
    if [[ $COUNTER -ge 18 ]]; then
        echo "Cannot allocate the resource."
        exit 1
    fi
else
    echo "Get into the critical section"
    touch $LOCK_FILE
fi

# critical section (check resources and take it/them)
RESOURCE=EMPTY
DEVICES_LIST=$(adb devices | awk -F" " '(match($1, /^[a-z0-9]/)) {printf "%s ", $1}')
for DEVICE in $DEVICES_LIST; do
    if [[ ! -f $DEVICE ]]; then
        RESOURCE=$DEVICE
        touch $RESOURCE
        break
    fi
done

# keep response in a file so that the
RESULT_FILE=RESULT
if [[ -f $RESULT_FILE ]]; then
    rm -rf $RESULT_FILE
fi
echo "ANDROID_SERIAL=$RESOURCE" > $RESULT_FILE

# release critical section
rm -rf $LOCK_FILE


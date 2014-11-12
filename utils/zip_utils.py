#!/usr/bin/env python
from zipfile import ZipFile
import os
import shutil

def modify_zipfile(zip_path, handlers, new_path="./"):
    # Backup zipfile
    ori_zip_path = zip_path + ".org"
    shutil.move(zip_path, ori_zip_path)
    with ZipFile(ori_zip_path, "r") as zipfile:
        zipfile.extractall(new_path)
        target_path = os.path.join(new_path, target_path)
        for h in handlers:
            h()
        # re-archive zip_path
        with ZipFile(zip_path, "w") as archive:
            for root, dirs, files in os.walk(new_path):
                for f in files:
                    f = os.path.join(root, f)
                    archive.write(f, os.path.relpath(f, new_path))

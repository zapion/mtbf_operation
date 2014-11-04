#!/usr/bin/python
import os
import sys
from github_utils import prepare_github_resource

def prepare_b2g_flash_tools(root_path="./", version=None):
    prepare_github_resource( "http://github.com/Mozilla-TWQA/B2G-flash-tool.git", root_path, version)

#!/bin/bash

# echo "Checking 'B2G-flash-tool' project..."
# if [[ -d ./B2G-flash-tool ]]; then
#     echo "Already have B2G-flash-tool folder."
# else
#     git clone http://github.com/Mozilla-TWQA/B2G-flash-tool.git
# fi
# cd B2G-flash-tool/
# git pull || echo "git pull failed at B2G-flash-tool."
# cd ..

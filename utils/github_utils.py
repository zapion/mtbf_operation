#!/usr/bin/python
import os
import sys

def prepare_github_resource(github_repo, root_path="./", version=None):
    project_name = github_repo.split("/")[-1].split(".")[0]
    project_path = os.path.join(path, prject_name)
    tool_exists = os.path.exist(project_path)
    sys.stdout.write("Checking " + project_name + " project....  " + str(tool_exists))
    if not tool_exists:
        os.system("cd " + root_path + " && git clone" + github_repo)
    os.system("cd " + project_path + " && git pull")
    if version:
        os.system("cd " + project_path + " && git checkout " + version)

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

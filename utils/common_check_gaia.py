#!/bin/python

from github_utils import prepare_github_resource

def prepare_gaia(root_path="./", version=None):
    prepare_github_resource("https://github.com/mozilla-b2g/gaia.git", root_path, version)

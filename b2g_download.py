#!/usr/bin/env python
import sys

try:
    from controller.console_controller import ConsoleApp
except ImportError:
    print("Can't find b2g flash tool ultilities.  Please run make b2g-flash-tool")
    sys.exit(1)

from utilities.logger import Logger
from utilities.path_parser import PathParser


class PvtDownloader(ConsoleApp):
    def run(self):
        while not self.auth.is_authenticated:
            # The init of BaseController will load .ldap file.
            # Get the Build Data into self.data obj.
            self.setAuth(self.account, self.password)
            if not self.auth.is_authenticated:
                self.account = ''
                self.password = ''

        # get target device
        devices = self.data.keys()
        # check device from load options
        if not self.target_device == '' and self.target_device not in devices:
            self.logger.log('The device [' + self.target_device + '] do not exist.', level=Logger._LEVEL_WARNING)
            self.target_device = ''
        elif not self.target_device == '' and self.target_device in devices:
            self.logger.log('The device [' + self.target_device + '] exist.')
        if self.target_device == '':
            self.logger.log('Invalid device', level=Logger._LEVEL_WARNING)
            self.quit()

        # get target branch
        branchs = self.data[self.target_device].keys()
        # check branch from load options
        if not self.target_branch == '' and self.target_branch not in branchs:
            self.logger.log('The branch [' + self.target_branch + '] of [' + self.target_device + '] do not exist.', level=Logger._LEVEL_WARNING)
            self.target_branch = ''
        elif not self.target_branch == '' and self.target_branch in branchs:
            self.logger.log('The branch [' + self.target_branch + '] of [' + self.target_device + '] exist.')
        if self.target_branch == '':
            self.logger.log('Invalid branch of [' + self.target_device + '].', level=Logger._LEVEL_WARNING)
            self.quit()

        # get target build
        builds = self.data[self.target_device][self.target_branch].keys()
        # check engineer/user build from load options
        if not self.target_build == '' and self.target_build not in builds:
            self.logger.log('The [' + self.target_build + '] build of [' + self.target_device + '] [' + self.target_branch + '] do not exist.', level=Logger._LEVEL_WARNING)
            self.target_build = ''
        elif not self.target_build == '' and self.target_build in builds:
            self.logger.log('The [' + self.target_build + '] build of [' + self.target_device + '] [' + self.target_branch + '] exist.')
        if self.target_build == '':
            self.logger.log('Invalid build of [' + self.target_device + '] [' + self.target_branch + '].', level=Logger._LEVEL_WARNING)
            self.quit()

        # Get the target build's information
        self.target_build_info = self.data[self.target_device][self.target_branch][self.target_build]

        self.latest_or_buildid = 'Latest'
        if not self.target_build_id == '':
            if self.pathParser.verify_build_id(self.target_build_id):
                self.latest_or_buildid = self.target_build_id
                self.logger.log('Set up the build ID [' + self.target_build_id + '] of [' + self.target_device + '] [' + self.target_branch + '].')
            else:
                self.logger.log('The build id [' + self.target_build_id + '] is not not valid.', level=Logger._LEVEL_WARNING)
                self.quit()
        else:
            self.logger.log('Set up the latest build of [' + self.target_device + '] [' + self.target_branch + '].')
            self.target_build_id = self.getLatestBuildId(self.target_build_info['src'])

        # get available packages
        packages = self.getPackages(self.target_build_info['src'], build_id=self.target_build_id)
        ## TODO: replace latest package with downloaded
        if len(packages) <= 0:
            self.logger.log('There is no flash package of [' + self.target_device + '] [' + self.target_branch + '] [' + self.target_build + '] [' + self.latest_or_buildid + ']  Build.', level=Logger._LEVEL_WARNING)
            self.quit()

        # setup the flash params from user selection
        self.flash_params.append(PathParser._IMAGES)
        self.flash_params.append(PathParser._GAIA)
        self.flash_params.append(PathParser._GECKO)

        # download
        self.logger.log(self.do_download(self.flash_params))

if __name__ == '__main__':
    pvtd = PvtDownloader()
    pvtd.run()

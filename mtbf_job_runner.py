#!/usr/bin/env python
import combo_runner.action_decorator
from combo_runner.base_action_runner import BaseActionRunner
from utils.zip_utils import modify_zipfile
import os


class MtbfJobRunner(BaseActionRunner):

    action = combo_runner.action_decorator.action

    def pre_flash(self):
        pass

    def flash(self):
        pass

    def post_flash(self):
        pass

#    @action
    def add_7mobile_action(self, action=False):
        # require import gaia_data_layer to call setSettings



if __name__ == '__main__':
    MtbfJobRunner().add_7mobile_action()

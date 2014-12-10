import os
from comborunner import action_decorator
from comborunner.base_action_runner import BaseActionRunner


class MTBFActionRunner(BaseActionRunner):

    action = action_decorator.action

    BRANCH_V210_KK = 'mozilla-b2g34_v2_1-flame-kk-eng'
    GECKO_B2G34    = 'b2g-34.0.en-US.android-arm.tar.gz'
    SYMBOLS_B2G34  = 'b2g-34.0.en-US.android-arm.crashreporter-symbols.zip'

    def __init__(self):
        os.environ['BRANCH']  = self.BRANCH_V210_KK
        os.environ['GECKO']   = self.GECKO_B2G34
        os.environ['SYMBOLS'] = self.SYMBOLS_B2G34
        os.environ['GAIA']    = 'gaia.zip'
        super(MTBFActionRunner, self).__init__()

    @action
    def download_pvt_b2g(self, action=False):
        if action:
            self.pre_commands.append('./mtbf_download_pvt_b2g.sh')
        return self

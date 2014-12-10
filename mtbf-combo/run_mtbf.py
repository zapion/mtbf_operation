#!/usr/bin/python

import os
from mtbf_action_runner import MTBFActionRunner


def main():
    runner = MTBFActionRunner()
    runner.download_pvt_b2g()
    runner.run()

if __name__ == '__main__':
    main()

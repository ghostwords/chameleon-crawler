#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2015 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from glob import glob
from os import path

import argparse


def is_valid_file(f, parser):
    if path.isfile(f):
        return f
    raise argparse.ArgumentTypeError("%s does not exist!" % f)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--crx", metavar='CRX_FILE_PATH', action="store",
            type=lambda x: is_valid_file(x, parser),
            default=max(glob("*.crx"), key=path.getmtime),
            help="path to Chrome extension CRX package")

    parser.add_argument("-n", dest='num_crawlers', type=int,
            choices=range(1, 9), default=2,
            help="number of parallel processes to use")

    parser.add_argument("--non-headless", action="store_true",
            help="do not use a virtual display")

    return parser.parse_args()

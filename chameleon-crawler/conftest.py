#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2014 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from glob import glob
from os import path

def is_valid_file(f, parser):
    if path.isfile(f):
        return f
    else:
        return parser.optparser.error("%s does not exist!" % f)


def pytest_addoption(parser):
    parser.addoption("--non-headless", action="store_true",
            help="do not use a virtual display")

    parser.addoption("--crx", metavar='CRX_FILE_PATH', action="store",
            type=lambda x: is_valid_file(x, parser),
            default=max(glob("*.crx"), key=path.getmtime),
            help="path to Chrome extension CRX package")

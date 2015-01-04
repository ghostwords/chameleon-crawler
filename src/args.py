#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2015 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from os import path

import argparse


def is_valid_file(f, parser):
    if path.isfile(f):
        return f
    raise argparse.ArgumentTypeError("%s does not exist!" % f)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("crx", metavar='CHAMELEON_CRX_FILE_PATH',
            type=lambda x: is_valid_file(x, parser),
            help="path to Chameleon CRX package")

    parser.add_argument("-n", dest='num_crawlers', type=int,
            choices=range(1, 9), default=2,
            help="parallel browser processes to use (default: %(default)s)")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--headless", action="store_true", default=True,
            help="use a virtual display (default)")
    group.add_argument("--no-headless", dest='headless', action="store_false")

    parser.add_argument("--timeout", metavar='SECONDS',
            type=int, default=20,
            help="seconds to wait for pages to finish "
                "before timing out (default: %(default)s)")

    parser.add_argument("--urls", metavar='URL_FILE_PATH',
            type=argparse.FileType('r'), default='urls.txt',
            help="path to URL list file (default: %(default)s)")

    return parser.parse_args()

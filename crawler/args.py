#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2016 ghostwords.
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

    parser.add_argument(
        "crx", metavar='CHAMELEON_CRX_FILE_PATH',
        type=lambda x: is_valid_file(x, parser),
        help="path to Chameleon CRX package"
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--headless", action="store_true", default=True,
        help="use a virtual display (default)"
    )
    group.add_argument("--no-headless", dest='headless', action="store_false")

    parser.add_argument(
        "-n", dest='num_crawlers', type=int,
        choices=range(1, 9), default=4,
        help="how many browsers to use in parallel "
        "(default: %(default)s)"
    )

    parser.add_argument(
        "-q", "--quiet", action="store_true", default=False,
        help="turn off standard output"
    )

    parser.add_argument(
        "-t", "--timeout", metavar='SECONDS',
        type=int, default=20,
        help="how many seconds to wait for pages to finish "
        "loading before timing out (default: %(default)s)"
    )

    parser.add_argument(
        "--urls", metavar='URL_FILE_PATH',
        type=argparse.FileType('r'), default='urls.txt',
        help="path to URL list file (default: %(default)s)"
    )

    return parser.parse_args()

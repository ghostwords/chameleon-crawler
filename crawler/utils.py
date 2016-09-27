#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2016 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from multiprocessing import Lock


class Logger(object):
    def __init__(self):
        self.lock = Lock()

    def log(self, *args, **kwargs):
        with self.lock:
            print(*args, **kwargs)

#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2015 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from time import sleep


def collect(result_queue, log):
    while True:
        if result_queue.empty():
            sleep(0.01)
            continue

        result = result_queue.get()

        if not result:
            break

        for url, data in result.items():
            log(url, ":", data['domains'].keys()
                if data is not None else "TIMED OUT")

    log("Collecting finished.")

#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2015 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from time import sleep

from .utils import DATABASE_URL

import dataset
import json


def collect(crawl_id, result_queue, log):
    with dataset.connect(DATABASE_URL) as db:
        while True:
            if result_queue.empty():
                sleep(0.01)
                continue

            result = result_queue.get()

            if result is None:
                break

            crawl_url, result = result

            page_url, data = None, None
            if result:
                [(page_url, data)] = result.items()
                data = json.dumps(data)

            db['result'].insert(dict(
                crawl_id=crawl_id,
                crawl_url=crawl_url,
                page_url=page_url,
                data=data
            ))

    log("Collecting finished.")
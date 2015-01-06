#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2015 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import datetime
from multiprocessing import Process, Queue
from urllib.parse import urlparse

from crawler.args import parse_args
from crawler.collector import collect
from crawler.crawler_manager import Crawler
from crawler.utils import DATABASE_URL, Logger

import dataset


def run():
    # store start time, plus get an ID for this crawl
    with dataset.connect(DATABASE_URL) as db:
        db['crawl'].insert(dict(start_time=datetime.now()))
        crawl_id = list(
            db['crawl'].find(_limit=1, order_by='-id')
        )[0]['id']

    # get commandline args
    args = parse_args()

    url_queue = Queue() # (url, num_timeouts) tuples
    result_queue = Queue()

    log = Logger().log

    # read in URLs and populate the job queue
    with args.urls:
        for url in args.urls:
            url = url.strip()
            if not urlparse(url).scheme:
                url = 'http://' + url
            url_queue.put((url, 0))

    # launch browsers
    crawlers = []
    for i in range(args.num_crawlers):
        crawler = Process(
            target=Crawler,
            args=(i + 1,),
            kwargs={
                'crx': args.crx,
                'headless': args.headless,
                'logger': log,
                'timeout': args.timeout,
                'url_queue': url_queue,
                'result_queue': result_queue
            }
        )
        crawler.start()
        crawlers.append(crawler)

    Process(target=collect, args=(crawl_id, result_queue, log)).start()

    # wait for all browsers to finish
    for crawler in crawlers:
        crawler.join()

    # tell collector we are done
    result_queue.put(None)

    # store completion time
    with dataset.connect(DATABASE_URL) as db:
        db['crawl'].update(dict(id=crawl_id, end_time=datetime.now()), 'id')

    log("Main process all done!")


if __name__ == '__main__':
    run()

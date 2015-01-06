#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2015 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from multiprocessing import Process, Queue
from urllib.parse import urlparse

from crawler.args import parse_args
from crawler.collector import collect
from crawler.crawler_manager import Crawler
from crawler.utils import Logger


def run():
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

    Process(target=collect, args=(result_queue, log)).start()

    # wait for all browsers to finish
    for crawler in crawlers:
        crawler.join()

    # tell collector process we are finished
    result_queue.put(None)

    log("Main process all done!")


if __name__ == '__main__':
    run()

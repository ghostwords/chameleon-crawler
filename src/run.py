#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2015 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from multiprocessing import Queue
from threading import Thread

from args import parse_args
from crawler import Crawler


def run():
    # get commandline args
    args = parse_args()

    url_queue = Queue() # (url, num_timeouts) tuples
    result_queue = Queue()

    # read in URLs and populate the job queue
    with open("urls.txt") as f:
        for url in f:
            url_queue.put((url.strip(), 0))

    # launch browsers
    crawlers = []
    for i in range(1, args.num_crawlers + 1):
        crawler = Thread(
            target=Crawler,
            args=(i, not args.non_headless),
            kwargs={
                'crx': args.crx,
                'url_queue': url_queue,
                'result_queue': result_queue
            }
        )
        crawler.start()
        crawlers.append(crawler)

    # wait for all browsers to finish
    for crawler in crawlers:
        crawler.join()

    # print results
    while not result_queue.empty():
        for url, data in result_queue.get().items():
            print(url, ":", data['domains'].keys()
                if data is not None else "TIMED OUT")


if __name__ == '__main__':
    run()

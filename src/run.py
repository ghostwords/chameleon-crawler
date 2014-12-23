#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2014 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from multiprocessing import Process, Queue

from args import parse_args
from crawler import Crawler


def run():
    url_queue = Queue()
    result_queue = Queue()

    # read in URLs and populate the job queue
    with open("urls.txt") as f:
        for url in f:
            url_queue.put(url.strip())

    # get commandline args
    args = parse_args()

    # launch browsers
    processes = []
    for i in range(args.num_crawlers):
        p = Process(
            target=Crawler,
            name="Crawler %i" % i,
            args=(not args.non_headless,),
            kwargs={
                'crx': args.crx,
                'url_queue': url_queue,
                'result_queue': result_queue
            }
        )
        p.start()
        processes.append(p)

    # wait for all browsers to finish
    for p in processes:
        p.join()

    # print results
    while not result_queue.empty():
        for url, data in result_queue.get().items():
            print(url, ":", data['domains'].keys())


if __name__ == '__main__':
    run()

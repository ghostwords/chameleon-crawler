#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2014 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from multiprocessing import Process, Queue

from crawler_process import CrawlerProcess

import os
import queue
import signal

TIMEOUT = 10


class Crawler(object):
    def __init__(self, id, headless=False, **kwargs):
        self.id = id
        self.headless = headless

        self.crx = kwargs['crx']
        self.glob_url_queue = kwargs['url_queue']
        self.glob_result_queue = kwargs['result_queue']

        self.url_queue = Queue()
        self.result_queue = Queue()

        self.start_process()

        while not self.glob_url_queue.empty():
            url, num_timeouts = self.glob_url_queue.get()

            self.url_queue.put(url)

            try:
                result = self.result_queue.get(True, TIMEOUT)

            except queue.Empty:
                print("%s timed out fetching %s" % (self.process.name, url))
                num_timeouts += 1

                # TODO fails to stop chromedriver/Xvfb when ???
                self.stop_process()

                if num_timeouts > 2:
                    print("Too many timeouts, giving up on %s" % url)
                    self.glob_result_queue.put({
                        url: None
                    })
                else:
                    self.glob_url_queue.put((url, num_timeouts))

                if not self.glob_url_queue.empty():
                    self.start_process()

            else:
                self.glob_result_queue.put(result)

        # tell the process we are done
        self.url_queue.put(None)

    def start_process(self):
        self.process = Process(
            target=CrawlerProcess,
            name="Crawler %i" % self.id,
            args=(self.headless,),
            kwargs={
                'crx': self.crx,
                'url_queue': self.url_queue,
                'result_queue': self.result_queue
            }
        )
        self.process.start()

    def stop_process(self):
        os.kill(self.process.pid, signal.SIGKILL)

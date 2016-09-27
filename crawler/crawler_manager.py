#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2016 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from multiprocessing import Process, Queue

from .crawler_process import CrawlerProcess

import os
import queue
import signal


class Crawler(object):
    def __init__(self, id, headless=True, timeout=20, **kwargs):
        self.id = id
        self.headless = headless

        self.crx = kwargs['crx']
        self.glob_url_queue = kwargs['url_queue']
        self.glob_result_queue = kwargs['result_queue']
        self.log = kwargs['logger']

        self.url_queue = Queue()
        self.result_queue = Queue()

        self.start_process()

        while not self.glob_url_queue.empty():
            url, num_timeouts = self.glob_url_queue.get()

            self.url_queue.put(url)

            try:
                error, result = self.result_queue.get(
                    True,
                    timeout * ((num_timeouts + 1) ** 2)
                )

            except queue.Empty:
                self.log("%s timed out fetching %s" % (self.process.name, url))
                num_timeouts += 1

                self.stop_process()

                if num_timeouts > 2:
                    self.log("Too many timeouts, giving up on %s" % url)
                    self.glob_result_queue.put((url, 'TIMEOUT', None))
                    reinserted = False
                else:
                    self.glob_url_queue.put((url, num_timeouts))
                    reinserted = True

                if reinserted or not self.glob_url_queue.empty():
                    self.start_process()

            else:
                self.glob_result_queue.put((url, error, result))

        # tell the process we are done
        self.url_queue.put(None)

    def start_process(self):
        name = "Crawler %i" % self.id
        self.log("Starting %s" % name)

        self.process = Process(
            target=CrawlerProcess,
            name=name,
            kwargs={
                'crx': self.crx,
                'headless': self.headless,
                'logger': self.log,
                'url_queue': self.url_queue,
                'result_queue': self.result_queue
            }
        )

        self.process.start()

        self.driver_pid, self.display_pid = self.result_queue.get()

    # TODO cross-platform termination (with psutil?)
    def stop_process(self):
        self.log("Stopping %s" % self.process.name)

        try:
            os.kill(self.process.pid, signal.SIGKILL)
        except ProcessLookupError:
            self.log("Crawler process not found.")

        try:
            os.kill(self.driver_pid, signal.SIGKILL)
        except ProcessLookupError:
            self.log("chromedriver process not found.")

        if self.headless:
            try:
                os.kill(self.display_pid, signal.SIGKILL)
            except ProcessLookupError:
                self.log("Xvfb process not found.")

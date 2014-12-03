#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2014 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest
#import socket
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
#from urllib.error import URLError
from xvfbwrapper import Xvfb

# TODO https://code.google.com/p/selenium/issues/detail?id=687
#socket.setdefaulttimeout(15)

class BaseTest(object):
    def setup_method(self, method):
        self.xvfb = not pytest.config.getoption('--non-headless')
        if self.xvfb:
            self.vdisplay = Xvfb(width=1440, height=900)
            self.vdisplay.start()

        opts = webdriver.chrome.options.Options()
        opts.add_extension(pytest.config.getoption('--crx'))
        self.driver = webdriver.Chrome(chrome_options=opts)
        self.driver.implicitly_wait(5)

        self.extension_id = self.get_extension_id()

    def teardown_method(self, method):
        self.collect_data()

        self.driver.quit()

        if self.xvfb and self.vdisplay:
            self.vdisplay.stop()

    def collect_data(self):
        # Chrome extension APIs just aren't there sometimes ...
        while True:
            self.get(
                "chrome-extension://%s/_generated_background_page.html" %
                self.extension_id)

            if self.js("return chrome.hasOwnProperty('tabs');"):
                break

        self.js("""chrome.tabs.query({}, function (tabs) {
            window.result = tabs.reduce(function (memo, tab) {
                var data = tabData.get(tab.id);
                if (data) {
                    memo[tab.id] = data;
                }
                return memo;
            }, {});
        });""")

        self.wait_for_script(
            "return typeof result == 'object' && !!result;")
        print(self.js("return result;"))

    def get(self, url):
        with self.new_window():
            return self.driver.get(url)

    def get_extension_id(self):
        self.driver.get("chrome://extensions-frame/")
        return self.driver.find_element_by_class_name(
            'extension-list-item-wrapper').get_attribute('id')

    def js(self, script):
        return self.driver.execute_script(script)

    @contextmanager
    def new_window(self):
        # TODO
        #self.js('window.open("about:blank");')
        #self.driver.switch_to_window(self.driver.window_handles[-1])
        yield

    def wait_for_script(self, script, timeout=5):
        return WebDriverWait(self.driver, timeout, poll_frequency=0.5).until(
            lambda drv: drv.execute_script(script),
            ("Timeout waiting for script to eval to True:\n%s" % script)
        )

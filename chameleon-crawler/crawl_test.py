#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2014 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from crawler import Crawler

import pytest

@pytest.yield_fixture
def urls():
    with open("urls.txt") as f:
        yield f.readlines()

class Test(Crawler):
    def test_visit_page(self, urls):
        for url in urls:
            self.get(url)

#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2015 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import dataset

DATABASE_URL = 'sqlite:///results.sqlite3'


def initialize_database():
    with open('results_schema.sql') as f:
        with dataset.connect(DATABASE_URL) as db:
            for sql in f.read().split(';'):
                db.query(sql)

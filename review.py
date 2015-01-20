#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2015 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from crawler.utils import DATABASE_URL
from reviewer.app import app


if __name__ == '__main__':
    app.config['DATABASE_URL'] = DATABASE_URL
    app.run(debug=True)

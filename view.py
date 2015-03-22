#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2015 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from flask_failsafe import failsafe

import dataset


@failsafe
def create_app():
    # imports of our code are inside this function so that Flask-Failsafe can
    # catch errors that happen at import time
    from crawler.utils import DATABASE_URL
    from viewer.app import app

    # initialize the db
    with open('results_schema.sql') as f:
        with dataset.connect(DATABASE_URL) as db:
            for sql in f.read().split(';'):
                db.query(sql)

    app.config['DATABASE_URL'] = DATABASE_URL
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    return app


if __name__ == '__main__':
    create_app().run(debug=True)

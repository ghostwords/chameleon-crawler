#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2016 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from flask_failsafe import failsafe


@failsafe
def create_app():
    # imports of our code are inside this function so that Flask-Failsafe can
    # catch errors that happen at import time
    from viewer.app import app

    return app


if __name__ == '__main__':
    create_app().run(debug=True)

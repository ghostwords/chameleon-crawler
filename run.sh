#!/usr/bin/env bash

# chameleon-crawler
#
# Copyright 2014 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

VIRTUALENV_NAME=chameleon-crawler

source `which virtualenvwrapper.sh`

if ! workon $VIRTUALENV_NAME 2>/dev/null; then
	mkvirtualenv -p `which python3` $VIRTUALENV_NAME
fi

trap 'deactivate $VIRTUALENV_NAME' EXIT

pip install -r requirements.txt

py.test chameleon-crawler -s "${@}"

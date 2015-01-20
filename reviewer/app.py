#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2015 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import datetime
from flask import Flask, render_template

import dataset

app = Flask(__name__)


def get_crawl_breakdown(crawl_id):
    statuses = []

    with dataset.connect(app.config['DATABASE_URL']) as db:
        result = db.query(
            """SELECT error, COUNT(DISTINCT crawl_url) AS num_urls
            FROM result WHERE crawl_id = :id GROUP BY error""",
            id=crawl_id
        ) if 'result' in db.tables else []

        for row in result:
            statuses.append({
                'error': row['error'],
                'num_urls': row['num_urls']
            })

    return statuses


def get_crawls():
    crawls = []

    with dataset.connect(app.config['DATABASE_URL']) as db:
        result = db.query(
            """SELECT
            crawl.id,
            COUNT(DISTINCT crawl_url) AS num_urls,
            (STRFTIME('%s', end_time) - STRFTIME('%s', start_time)) / 60
                AS duration,
            STRFTIME('%s', start_time) AS start_time
            FROM crawl
            JOIN result ON result.crawl_id = crawl.id
            GROUP BY crawl.id
            ORDER BY crawl.id DESC"""
        ) if 'crawl' in db.tables else []

        for row in result:
            crawls.append({
                'id': row['id'],
                'num_urls': row['num_urls'],
                'duration': row['duration'],
                'start_time': datetime.utcfromtimestamp(
                    int(row['start_time'])).strftime("%I:%M %p %b %d %Y"),
            })

    return crawls


@app.route('/crawl/<int:crawl_id>')
def crawl(crawl_id):
    return render_template(
        'crawl.html',
        crawl_id=crawl_id,
        crawl_breakdown=get_crawl_breakdown(crawl_id)
    )


@app.route('/')
def index():
    return render_template(
        'crawls.html',
        crawls=get_crawls()
    )

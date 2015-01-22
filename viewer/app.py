#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2015 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import datetime
from flask import Flask, render_template, request

import dataset

app = Flask(__name__)


def get_fingerprinters(crawl_ids):
    if crawl_ids:
        in_clause = "AND crawl_id IN (%s)" % ','.join(
            [str(int(id)) for id in crawl_ids])

    sql = """SELECT
            crawl_url,
            script_url,
            script_domain,
            canvas,
            font_enum,
            navigator_enum
        FROM result
        WHERE (canvas = 1 OR font_enum = 1 OR navigator_enum = 1) %s
        GROUP BY
            crawl_url,
            script_url,
            script_domain,
            canvas,
            font_enum,
            navigator_enum
        ORDER BY
            script_domain""" % (in_clause if crawl_ids else "")

    with dataset.connect(app.config['DATABASE_URL']) as db:
        result = db.query(sql)
        return list(result)


def get_problem_pages(crawl_ids):
    if crawl_ids:
        in_clause = "AND crawl_id IN (%s)" % ','.join(
            [str(int(id)) for id in crawl_ids])

    sql = """SELECT crawl_url, error, COUNT(*) count
        FROM result
        WHERE error IS NOT NULL %s
        GROUP BY crawl_url, error
        ORDER BY count DESC""" % (in_clause if crawl_ids else "")

    with dataset.connect(app.config['DATABASE_URL']) as db:
        result = db.query(sql)
        return list(result)


def get_crawl_errors():
    errors = {}

    with dataset.connect(app.config['DATABASE_URL']) as db:
        result = db.query(
            """SELECT crawl_id, error, COUNT(DISTINCT crawl_url) num_urls
            FROM result
            WHERE error IS NOT NULL
            GROUP BY crawl_id, error"""
        ) if 'result' in db.tables else []

        for row in result:
            errors.setdefault(
                row['crawl_id'], {})[row['error']] = row['num_urls']

    return errors


def get_crawls():
    with dataset.connect(app.config['DATABASE_URL']) as db:
        result = db.query(
            """SELECT
            crawl.id,
            COUNT(DISTINCT crawl_url) num_urls,
            (STRFTIME('%s', end_time) - STRFTIME('%s', start_time)) duration,
            STRFTIME('%s', start_time) start_time
            FROM crawl
            JOIN result ON result.crawl_id = crawl.id
            GROUP BY crawl.id
            ORDER BY crawl.id DESC"""
        ) if 'crawl' in db.tables else []

        return list(result)


@app.route('/results')
def results():
    crawl_ids = [int(i) for i in request.values.getlist('crawl')]

    return render_template(
        'results.html',
        fingerprinters=get_fingerprinters(crawl_ids),
        problem_pages=get_problem_pages(crawl_ids)
    )


@app.route('/')
def index():
    crawls = get_crawls()

    for crawl in crawls:
        crawl['start_time'] = datetime.utcfromtimestamp(
            int(crawl['start_time'])).strftime("%I:%M %p %b %d %Y")

    return render_template(
        'crawls.html',
        crawls=crawls,
        errors=get_crawl_errors()
    )

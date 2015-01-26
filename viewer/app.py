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


def get_fingerprinters(crawl_ids=None, canvas=True, font_enum=True,
        navigator_enum=True, num_properties=4):
    fp = {}

    in_clause = ""
    if crawl_ids:
        in_clause = "AND crawl_id IN (%s)" % ','.join(
            [str(int(id)) for id in crawl_ids])

    filters = []
    if canvas:
        filters.append("canvas = 1")
    if font_enum:
        filters.append("font_enum = 1")
    if navigator_enum:
        filters.append("navigator_enum = 1")
    if num_properties:
        filters.append("num_properties >= %s" % str(int(num_properties)))

    having_clause = ""
    if filters:
        having_clause = "HAVING %s" % " OR ".join(filters)

    sql = """SELECT * FROM (
        SELECT
            result.*,
            COUNT(pc.result_id) num_properties
        FROM result
        LEFT JOIN property_count pc ON pc.result_id = result.id
        WHERE 1 {in_clause}
        GROUP BY COALESCE(pc.result_id, result.id)
        {having_clause}
    ) GROUP BY
        crawl_url,
        page_url,
        script_url,
        canvas,
        font_enum,
        navigator_enum,
        num_properties""" \
    .format(in_clause=in_clause, having_clause=having_clause)

    with dataset.connect(app.config['DATABASE_URL']) as db:
        result = db.query(sql)

        """ {
            row['script_domain']: {
                row['script_url']: [
                    row,
                    ...
                ],
                ...
            },
            ...
        }"""
        for row in result:
            fp.setdefault(row['script_domain'], {}).setdefault(
                row['script_url'], []).append(row)

    return fp


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


@app.template_filter('number_format')
def number_format(value):
    return '{:,}'.format(value)


@app.route('/errors')
def errors():
    crawl_ids = [int(i) for i in request.args.getlist('crawl')]

    return render_template(
        'errors.html',
        problem_pages=get_problem_pages(crawl_ids)
    )


@app.route('/results')
def results():
    crawl_ids = [int(i) for i in request.args.getlist('crawl')]

    filters = request.args.getlist('filter')

    num_properties = 4
    if filters:
        if 'num_properties' in filters:
            num_properties = request.args.get('num_properties')
        else:
            num_properties = False

    return render_template(
        'results.html',
        fingerprinters=get_fingerprinters(
            crawl_ids=crawl_ids,
            canvas='canvas' in filters if filters else True,
            font_enum='font_enum' in filters if filters else True,
            navigator_enum='navigator_enum' in filters if filters else True,
            num_properties=num_properties
        )
    )


@app.route('/')
def index():
    crawls = get_crawls()

    for crawl in crawls:
        crawl['start_time'] = datetime.utcfromtimestamp(
            int(crawl['start_time'])).strftime("%b %d %Y %I:%M %p")

    return render_template(
        'crawls.html',
        crawls=crawls,
        errors=get_crawl_errors()
    )
